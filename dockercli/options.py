from __future__ import unicode_literals

from optparse import OptionParser
from .option import CommandOption

COMMAND_NAMES = [
    'help',
    'version',
    'ps',
    'images',
    'run',
    'rm',
    'search',
    'start',
    'stop',
    'info'
]

COMMAND_OPTIONS = {
    'ps': [
        CommandOption(CommandOption.TYPE_BOOLEAN, '-a', '--all',
                      action='store_true',
                      dest='all',
                      help='Show all containers. '
                           'Only running containers are shown by default.'),
        CommandOption(CommandOption.TYPE_CONTAINER, None, '--before',
                      action='store',
                      dest='before',
                      help='Show only container created before Id or Name, ' +
                           'include non-running ones.'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-h', '--help',
                      action='store_true',
                      dest='help',
                      help='Display help for this command.'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-l', '--latest',
                      action='store_true',
                      dest='latest',
                      help='Show only the latest created container, ' +
                           'include non-running ones.'),
        CommandOption(CommandOption.TYPE_NUMERIC, '-n', None,
                      action='store',
                      dest='limit',
                      help='Show n last created containers, include ' +
                           'non-running ones.'),
        CommandOption(CommandOption.TYPE_NUMERIC, '--no-trunc', None,
                      action='store_false',
                      dest='trunc',
                      help='Don\'t truncate output.'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-q', '--quiet',
                      action='store_true',
                      dest='quiet',
                      help='Only display numeric IDs.'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-s', '--size',
                      action='store_true',
                      dest='latest',
                      help='Display total file sizes.'),
        CommandOption(CommandOption.TYPE_CONTAINER, None, '--since',
                      action='store',
                      dest='since',
                      help='Show only containers created since Id or Name, ' +
                           'include non-running ones.')
    ],
    'images': [
        CommandOption(CommandOption.TYPE_BOOLEAN, '-a', '--all',
                      action='store_true',
                      dest='all',
                      help='Show all images (by default filter out the ' +
                           'intermediate image layers).'),
        CommandOption(CommandOption.TYPE_IMAGE, '-f', '--filter',
                      action='store',
                      dest='name',
                      help='Provide name to filter on.'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-h', '--help',
                      action='store_true',
                      dest='help',
                      help='Display help for this command.'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-q', '--quiet',
                      action='store_true',
                      dest='quiet',
                      help='Only show numeric IDs.')
    ],
    'run': [
        CommandOption(CommandOption.TYPE_BOOLEAN, '-d', '--detach',
                      action='store_true',
                      dest='detach',
                      help='Detached mode: run the container in the ' +
                           'background and print the new container ID'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-h', '--help',
                      action='store_true',
                      dest='help',
                      help='Display help for this command.'),
        CommandOption(CommandOption.TYPE_CONTAINER, '--name',
                      action='store',
                      dest='name',
                      help='Assign a name to the container.'),
        CommandOption(CommandOption.TYPE_IMAGE, 'image',
                      action='store',
                      help='Image ID or name to use.'),
        CommandOption(CommandOption.TYPE_COMMAND, 'command',
                      action='store',
                      help='Command to run in a container.'),
    ],
    'start': [
        CommandOption(CommandOption.TYPE_BOOLEAN, '-a', '--attach',
                      action='store_true',
                      dest='attach',
                      help='Attach container\'s STDOUT and STDERR and ' +
                           'forward all signals to the process.',
                      no_match=True),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-h', '--help',
                      action='store_true',
                      dest='help',
                      help='Display help for this command.'),
        CommandOption(CommandOption.TYPE_CONTAINER, 'container',
                      action='store',
                      help='Container ID or name to use.'),
    ],
    'rm': [
        CommandOption(CommandOption.TYPE_CONTAINER, 'container',
                      action='store',
                      help='Container ID or name to use.',
                      nargs='+'),
        CommandOption(CommandOption.TYPE_BOOLEAN, '-h', '--help',
                      action='store_true',
                      dest='help',
                      help='Display help for this command.'),
    ],
    'search': [
        CommandOption(CommandOption.TYPE_BOOLEAN, '-h', '--help',
                      action='store_true',
                      dest='help',
                      help='Display help for this command.'),
        CommandOption(CommandOption.TYPE_IMAGE, 'term',
                      action='store',
                      help='A term to search for.'),
    ]
}


def find_option(command, name):
    """
    Helper method to find command option by its name.
    :param command: string
    :param name: string
    :return: CommandOption
    """
    if command in COMMAND_OPTIONS:
        for opt in COMMAND_OPTIONS[command]:
            if opt.name == name:
                return opt
    return None


def allowed_args(cmd, **kwargs):
    """
    Return only arguments that the command accepts.
    :param cmd: string
    :param kwargs: dict
    :return: dict
    """
    matches = {}
    available = all_options(cmd)
    if available:
        for k in kwargs:
            if k in available:
                matches[k] = kwargs[k]
    return matches


def all_options(command):
    """
    Helper method to find all command options that docker-py supports.
    :param command: string
    :return: set of CommandOption
    """
    result = set([])
    if command in COMMAND_OPTIONS:
        for opt in COMMAND_OPTIONS[command]:
            if opt.matches:
                result.add(opt.dest)
    return result


def parse_command_options(cmd, params):
    """
    Parse options for a given command.
    :param cmd: string: command name
    :param params: list: all tokens after command name
    :return: parser, args, opts
    """
    parser = OptParser(prog=cmd, add_help_option=False)
    for opt in COMMAND_OPTIONS[cmd]:
        if opt.name.startswith('-'):
            parser.add_option(*opt.args, **opt.kwargs)
    popts, pargs = parser.parse_args(params)
    popts = vars(popts)
    return parser, popts, pargs


def format_command_help(cmd):
    """
    Format help string for the command.
    :param cmd: string: command name
    :return: string
    """
    usage = [cmd, '[options]']

    for opt in COMMAND_OPTIONS[cmd]:
        if not opt.name.startswith('-'):
            usage.append(opt.name)

    usage = ' '.join(usage)

    parser = OptParser(prog=cmd, add_help_option=False, usage=usage)

    for opt in COMMAND_OPTIONS[cmd]:
        if opt.name.startswith('-'):
            parser.add_option(*opt.args, **opt.kwargs)

    return parser.format_help()


class OptParser(OptionParser):
    """
    Wrapper around OptionParser.
    Overrides error method to throw an exception.
    """
    def error(self, msg):
        """error(msg : string)

        Print a usage message incorporating 'msg' to stderr and exit.
        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        raise Exception("Error parsing options: {0}".format(msg))
