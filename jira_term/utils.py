import click
from jira import JIRAError


def get_self(cli):
    try:
        _self = cli.jira.myself()['name']
        return _self
    except JIRAError:
        click.echo(
            click.style(
                'Passed "me" as the assignee. Unable to get information for the current user.',
                fg='yellow',
            )
        )



def list_inner(cli, config, project, assignee, assignees, start_at, statuses, labels, label_operator, reporter, reporters, format, headers):
    jql = []

    if project:
        jql.append('project={}'.format(project))

    if assignee:
        assignees = [assignee]
        del assignee

    if assignees:
        _assignee_jql = []
        for assignee in assignees:
            if assignee == 'me':
                assignee = get_self(cli)

            _assignee_jql.append('assignee={}'.format(assignee))

        jql.append('({})'.format(' OR '.join(_assignee_jql)))

    if reporter:
        reporters = [reporter]
        del reporter

    if reporters:
        _reporter_jql = []
        for reporter in reporters:
            if reporter == 'me':
                reporter = get_self(cli)

            _reporter_jql.append('reporter={}'.format(reporter))

        jql.append('({})'.format(' OR '.join(_reporter_jql)))

    if statuses:
        _status_jql = []
        for status in statuses:
            _status_jql.append('status={}'.format(status))

        jql.append('({})'.format(' OR '.join(_status_jql)))

    if labels:
        _label_jql = []
        for label in labels:
            _label_jql.append('labels={}'.format(label))

        jql.append('({})'.format(' {} '.format(label_operator).join(_label_jql)))

    _jql = ' AND '.join(jql)
    print '_JQL', _jql

    issues = cli.jira.search_issues(_jql, startAt=start_at)

    if format == 'table' and headers:
        from tabulate import tabulate
        issues_table = []
        for issue in issues:
            issue_row = []
            for header in headers:
                if header == 'key':
                    issue_row.append(issue.key)

                if header == 'summary':
                    issue_row.append(issue.fields.summary)

                if header == 'labels':
                    issue_row.append(', '.join(issue.fields.labels))

                if header == 'assignee':
                    issue_row.append(issue.fields.assignee)

                if header == 'reporter':
                    issue_row.append(issue.fields.reporter)

            issues_table.append(issue_row)
        click.echo(tabulate(issues_table, headers=[click.style(header.upper(), bold=True) for header in headers], tablefmt='fancy_grid'))
    elif format == 'list':
        for issue in issues:
            click.echo('{}: {}'.format(issue.key, issue.fields.summary.encode('utf-8')))

    total = issues.total
    total_returned = len(issues)
    new_start_at = (issues.startAt + total_returned)

    if new_start_at < total:
        if click.confirm('View the next page of results?', abort=True):
            list_inner(cli, config, project, assignee, assignees, new_start_at, statuses, labels, label_operator, reporter, reporters, format, headers)
