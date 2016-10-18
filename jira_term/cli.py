import click
from jira import JIRA, JIRAError

from .config import pass_config
from .utils import get_self, list_inner


@click.group()
@pass_config
@click.pass_context
def cli(ctx, config,):
    config.load()

    if not ctx.invoked_subcommand == 'config':
        config._setup()
        config.load()

    try:
        cli.jira = JIRA(config['domain'], basic_auth=(config['username'], config['password']))
    except:
        pass


@cli.group()
@pass_config
def config(config):
    pass


@config.command()
@pass_config
@click.option('--username', '-u')
@click.option('--password', '-pw')
@click.option('--domain', '-d')
@click.option('--project', '-p')
@click.option('--type', '-t')
@click.option('--assignee')
def set(config, username, password, domain, project, type, assignee):
    if username:
        config['username'] = username

    if password:
        config['password'] = password

    if domain:
        config['domain'] = domain

    if project:
        config['project'] = project

    if type:
        config['type'] = type

    if assignee:
        config['assignee'] = assignee

    config.save()
    config.load()




@cli.group()
@pass_config
def issues(config):
    pass

@issues.command()
@pass_config
@click.option('--project', '-p')
@click.option('--assignee')
@click.option('--assignees', multiple=True)
@click.option('--start_at', '-sa', default=0, type=int)
@click.option('--statuses', '-s', multiple=True)
@click.option('--labels', '-l', multiple=True)
@click.option('--label_operator', default='OR', type=click.Choice(['OR', 'AND']))
@click.option('--reporter')
@click.option('--reporters', '-r', multiple=True)
@click.option('--format', '-f', default='list', type=click.Choice(['list', 'table']))
@click.option('--headers', '-h', multiple=True, type=click.Choice(['key', 'summary', 'labels', 'assignee', 'reporter']))
def list(config, project, assignee, assignees, start_at, statuses, labels, label_operator, reporter, reporters, format, headers):
    list_inner(cli, config, project, assignee, assignees, start_at, statuses, labels, label_operator, reporter, reporters, format, headers)


@issues.command()
@pass_config
@click.option('--project', '-p')
@click.option('--summary', '-s', required=True)
@click.option('--description', '-d', default='')
@click.option('--type', '-t')
@click.option('--attachments', '-a', multiple=True, type=click.File('rb'))
@click.option('--assignee')
@click.option('--reporter', '-r')
@click.option('--labels', '-l', multiple=True)
def create(config, project, summary, description, type, attachments, assignee, labels, reporter):
    project = project or config.get('project')
    type = type or config.get('type')
    assignee = assignee or config.get('assignee')

    if not project:
        click.echo(
            click.style(
                'Please supply a project in the config or pass --project to this command.',
                fg='red',
            )
        )
        return False

    if not type:
        click.echo(
            click.style(
                'Please supply a project in the config or pass --type to this command.',
                fg='red',
            )
        )
        return False

    optional_kwargs = {}

    if assignee:
        if assignee == 'me':
            assignee = get_self(cli)

        optional_kwargs['assignee'] = {'name': assignee}

    if reporter:
        if reporter == 'me':
            reporter = get_self(cli)

        optional_kwargs['reporter'] = {'name': reporter}

    try:
        issue = cli.jira \
            .create_issue(
                project=project,
                summary=summary,
                description=description,
                issuetype={'name': type},
                labels=labels,
                **optional_kwargs
            )

        url = '{}/browse/{}'.format(config['domain'], issue.key)
        click.echo(
            click.style(
                'Issue created!',
                fg='green',
            ),
        )
        click.echo('View issue: {}'.format(url))
    except JIRAError as e:
        extra_message = ''
        if 'issue type is required' in e.text:
            extra_message = 'For a list of available issue types, run `jira-cli issues types list`'

        click.echo(
            click.style(
                '{} \n{}'.format(str(e.text), extra_message),
                fg='red',
            )
        )

        return False

    if attachments:
        with click.progressbar(attachments, label='Uploading attachments', length=len(attachments)) as bar:
            for attachment in attachments:
                try:
                    cli.jira.add_attachment(issue=issue, attachment=attachment)
                    bar.update(1)  # this progress bar represents total attachments uploaded, not total bytes uploaded
                except JIRAError as e:
                    click.echo(
                        click.style(
                            '{}'.format(str(e.text)),
                            fg='red',
                        )
                    )
