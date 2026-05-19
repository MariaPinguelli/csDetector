import git
import csv
import os
import calendar
from collections import defaultdict

from dateutil.relativedelta import relativedelta
from typing import List
from progress.bar import Bar
from datetime import datetime
from utils import author_id_extractor
from statsAnalysis import output_statistics
from sentistrength import PySentiStr
from git.objects.commit import Commit
from configuration import Configuration
import pytz
import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)


def commit_analysis(
    senti: PySentiStr,
    commits: List[git.Commit],
    delta: relativedelta,
    config: Configuration,
):

    # sort commits
    commits.sort(key=lambda o: o.committed_datetime)

    # split commits into batches
    batches = []
    batch = []
    startDate = None
    endDate = None
    if config.startDate is not None:
        startDate = datetime.strptime(config.startDate, "%Y-%m-%d")
        startDate = startDate.replace(tzinfo=pytz.UTC)
    if config.endDate is not None:
        endDate = datetime.strptime(config.endDate, "%Y-%m-%d")
        endDate = endDate.replace(tzinfo=pytz.UTC)
        
    batch_dates = []

    commits_by_month = defaultdict(list)
    
    for commit in commits:
        if startDate is not None and startDate > commit.committed_datetime:
            continue
        if endDate is not None and endDate < commit.committed_datetime:
            continue
            
        # Chave única para cada mês/ano
        month_key = (commit.committed_datetime.year, commit.committed_datetime.month)
        commits_by_month[month_key].append(commit)
    
    # Ordenar os meses cronologicamente
    sorted_months = sorted(commits_by_month.keys())
    
    # Criar batches baseados no delta
    current_batch = []
    current_batch_start = None
    
    for i, month_key in enumerate(sorted_months):
        year, month = month_key
        month_commits = commits_by_month[month_key]
        
        # Data do primeiro commit deste mês (para batch_dates)
        first_commit_date = month_commits[0].committed_datetime.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        
        if current_batch_start is None:
            # Primeiro batch
            current_batch_start = first_commit_date
            current_batch.extend(month_commits)
        else:
            # Verificar se este mês ainda está dentro do delta do batch atual
            months_diff = (year - current_batch_start.year) * 12 + (month - current_batch_start.month)
            
            if months_diff < delta.months:
                # Ainda dentro do mesmo batch - adicionar commits
                current_batch.extend(month_commits)
            else:
                # Batch completo - salvar e começar novo
                batches.append(current_batch)
                batch_dates.append(current_batch_start)
                
                # Novo batch
                current_batch = list(month_commits)
                current_batch_start = first_commit_date
    
    # Adicionar o último batch
    if current_batch:
        batches.append(current_batch)
        batch_dates.append(current_batch_start)

    # run analysis per batch
    author_info_dict = {}
    days_active = list()
    for idx, batch in enumerate(batches):
        if batch:  # Só analisar batches não vazios
            batch_author_info_dict, batch_days_active = commit_batch_analysis(
                idx, senti, batch, config
            )
            author_info_dict.update(batch_author_info_dict)
            days_active.append(batch_days_active)
        else:
            days_active.append(0)

    return batch_dates, author_info_dict, days_active


def commit_batch_analysis(
    idx: int, senti: PySentiStr, commits: List[git.Commit], config: Configuration
):

    author_info_dict = {}
    timezone_info_dict = {}
    experience_days = 150

    # traverse all commits
    logger.info("Analyzing commits")
    startDate = None
    if config.startDate is not None:
        startDate = datetime.strptime(config.startDate, "%Y-%m-%d")
        startDate = startDate.replace(tzinfo=pytz.UTC)
    # sort commits
    commits.sort(key=lambda o: o.committed_datetime, reverse=True)

    commit_messages = []
    commit: Commit
    last_date = None
    first_date = None
    real_commit_count = 0
    for commit in Bar("Processing").iter(commits):
        if startDate is not None and startDate > commit.committed_datetime:
            continue
        if last_date is None:
            last_date = commit.committed_date
        first_date = commit.committed_date
        real_commit_count = real_commit_count + 1
        # extract info
        author = author_id_extractor(commit.author)
        timezone = commit.author_tz_offset
        time = commit.authored_datetime

        # get timezone
        timezone_info = timezone_info_dict.setdefault(
            timezone, dict(commitCount=0, authors=set())
        )

        # save info
        timezone_info["authors"].add(author)

        if commit.message and commit.message.strip():
            commit_messages.append(commit.message)

        # increase commit count
        timezone_info["commitCount"] += 1

        # get author
        author_info = author_info_dict.setdefault(
            author,
            dict(
                commitCount=0,
                sponsoredCommitCount=0,
                earliestCommitDate=time,
                latestCommitDate=time,
                sponsored=False,
                activeDays=0,
                experienced=False,
            ),
        )

        # increase commit count
        author_info["commitCount"] += 1

        # validate earliest commit
        # by default GitPython orders commits from latest to earliest
        if time < author_info["earliestCommitDate"]:
            author_info["earliestCommitDate"] = time

        # check if commit was between 9 and 5
        if commit.author_tz_offset != 0 and 9 <= time.hour <= 17:
            author_info["sponsoredCommitCount"] += 1

    logger.info("Analyzing commit message sentiment")
    sentiment_scores = []
    commit_message_sentiments_positive = []
    commit_message_sentiments_negative = []

    if len(commit_messages) > 0:
        sentiment_scores = senti.getSentiment(commit_messages)
        commit_message_sentiments_positive = list(
            result for result in filter(lambda value: value >= 1, sentiment_scores)
        )
        commit_message_sentiments_negative = list(
            result for result in filter(lambda value: value <= -1, sentiment_scores)
        )

    logger.info("Analyzing authors")
    sponsored_author_count = 0
    for login, author in author_info_dict.items():

        # check if sponsored
        commit_count = int(author["commitCount"])
        sponsored_commit_count = int(author["sponsoredCommitCount"])
        diff = sponsored_commit_count / commit_count
        if diff >= 0.95:
            author["sponsored"] = True
            sponsored_author_count += 1

        # calculate active days
        earliest_date = author["earliestCommitDate"]
        latest_date = author["latestCommitDate"]
        active_days = (latest_date - earliest_date).days + 1
        author["activeDays"] = active_days

        # check if experienced
        if active_days >= experience_days:
            author["experienced"] = True

    # calculate percentage sponsored authors
    percentage_sponsored_authors = sponsored_author_count / \
        len([*author_info_dict])

    # calculate active project days
    first_commit_date = None
    last_commit_date = None
    if first_date is not None:
        first_commit_date = datetime.fromtimestamp(first_date)
    if last_date is not None:
        last_commit_date = datetime.fromtimestamp(last_date)
    days_active = 0
    if last_commit_date is not None:
        days_active = (last_commit_date - first_commit_date).days

    logger.info("Outputting CSVs")

    # output author days on project
    with open(
        os.path.join(config.metricsPath, f"authorDaysOnProject_{idx}.csv"),
        "a",
        newline="",
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Author", "# of Days"])
        for login, author in author_info_dict.items():
            w.writerow([login, author["activeDays"]])

    # output commits per author
    with open(
        os.path.join(config.metricsPath, f"commitsPerAuthor_{idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Author", "Commit Count"])
        for login, author in author_info_dict.items():
            w.writerow([login, author["commitCount"]])

    # output timezones
    with open(
        os.path.join(config.metricsPath, f"timezones_{idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Timezone Offset", "Author Count", "Commit Count"])
        for key, timezone in timezone_info_dict.items():
            w.writerow([key, len(timezone["authors"]),
                       timezone["commitCount"]])

    # output results
    with open(
        os.path.join(config.resultsPath, f"results_{idx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["CommitCount", real_commit_count])
        w.writerow(["DaysActive", days_active])
        w.writerow(
            ["FirstCommitDate", "{:%Y-%m-%d}".format(first_commit_date)])
        w.writerow(["LastCommitDate", "{:%Y-%m-%d}".format(last_commit_date)])
        w.writerow(["AuthorCount", len([*author_info_dict])])
        w.writerow(["SponsoredAuthorCount", sponsored_author_count])
        w.writerow(["PercentageSponsoredAuthors",
                   percentage_sponsored_authors])
        w.writerow(["TimezoneCount", len([*timezone_info_dict])])

    output_statistics(
        idx,
        [author["activeDays"] for login, author in author_info_dict.items()],
        "AuthorActiveDays",
        config.resultsPath,
    )

    output_statistics(
        idx,
        [author["commitCount"] for login, author in author_info_dict.items()],
        "AuthorCommitCount",
        config.resultsPath,
    )

    output_statistics(
        idx,
        [len(timezone["authors"])
         for key, timezone in timezone_info_dict.items()],
        "TimezoneAuthorCount",
        config.resultsPath,
    )

    output_statistics(
        idx,
        [timezone["commitCount"]
            for key, timezone in timezone_info_dict.items()],
        "TimezoneCommitCount",
        config.resultsPath,
    )

    output_statistics(
        idx,
        sentiment_scores,
        "CommitMessageSentiment",
        config.resultsPath,
    )

    output_statistics(
        idx,
        commit_message_sentiments_positive,
        "CommitMessageSentimentsPositive",
        config.resultsPath,
    )

    output_statistics(
        idx,
        commit_message_sentiments_negative,
        "CommitMessageSentimentsNegative",
        config.resultsPath,
    )

    return author_info_dict, days_active