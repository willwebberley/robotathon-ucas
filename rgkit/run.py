#!/usr/bin/env python2

import argparse
from argparse import RawTextHelpFormatter
import ast
import copy
import imp
import inspect
import pkg_resources
import random
import os
import sys

try:
    imp.find_module('rgkit')
except ImportError:
    # force rgkit to appear as a module when run from current directory
    from os.path import dirname, abspath
    cdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
    parentdir = dirname(cdir)
    sys.path.insert(0, parentdir)

from rgkit.settings import settings as default_settings
from rgkit import game
from rgkit.game import Player


class Options:
    def __init__(self, map_filepath=None, print_info=False,
                 animate_render=False, play_in_thread=False, curses=False,
                 game_seed=None, match_seeds=None, quiet=0, symmetric=False,
                 n_of_games=1):

        if map_filepath is None:
            map_filepath = os.path.join(os.path.dirname(__file__),
                                        'maps/default.py')
        self.map_filepath = map_filepath
        self.print_info = print_info
        self.animate_render = animate_render
        self.play_in_thread = play_in_thread
        self.curses = curses
        self.game_seed = game_seed
        self.match_seeds = match_seeds
        self.quiet = quiet
        self.symmetric = symmetric
        self.n_of_games = n_of_games

    def __eq__(self, other):
        return (self.map_filepath == other.map_filepath and
                self.print_info == other.print_info and
                self.animate_render == other.animate_render and
                self.play_in_thread == other.play_in_thread and
                self.curses == other.curses and
                self.match_seeds == other.match_seeds and
                self.quiet == other.quiet and
                self.n_of_games == other.n_of_games and
                self.symmetric == other.symmetric)


class Runner:
    def __init__(self, player1=None, player2=None, player1_file=None,
                 player2_file=None, settings=None, options=None,
                 delta_callback=None):

        if settings is None:
            settings = Runner.default_settings()
        if options is None:
            options = Options()

        self._map_data = ast.literal_eval(open(options.map_filepath).read())
        self.settings = settings
        self.settings.init_map(self._map_data)
        # Players can only be initialized from file after initializing settings
        if player1_file is not None:
            player1 = self._make_player(player1_file)
        if player2_file is not None:
            player2 = self._make_player(player2_file)
        self._players = [player1, player2]
        self._delta_callback = delta_callback
        self._names = [player1.name(), player2.name()]
        self.options = options

        if Runner.is_multiprocessing_supported():
            import multiprocessing
            self._rgcurses_lock = multiprocessing.Lock()
        else:
            self._rgcurses_lock = None

    @staticmethod
    def from_robots(robot1, robot2, settings=None, options=None,
                    delta_callback=None):

        return Runner(player1=Player(robot=robot1),
                      player2=Player(robot=robot2),
                      settings=settings, options=options,
                      delta_callback=delta_callback)

    @staticmethod
    def from_command_line_args(args):
        map_name = os.path.join(args.map)

        options = Options(map_filepath=map_name,
                          print_info=not args.headless,
                          n_of_games=args.count,
                          animate_render=args.animate,
                          play_in_thread=args.play_in_thread,
                          quiet=args.quiet,
                          curses=args.curses,
                          match_seeds=args.match_seeds,
                          symmetric=args.symmetric)
        return Runner(player1_file=args.player1, player2_file=args.player2,
                      options=options)

    @staticmethod
    def _make_player(file_name):
        try:
            with open(file_name) as f:
                return game.Player(code=f.read())
        except IOError, msg:
            if pkg_resources.resource_exists('rgkit', file_name):
                bot_filename = pkg_resources.resource_filename('rgkit',
                                                               file_name)
                with open(bot_filename) as f:
                    return game.Player(code=f.read())
            raise IOError(msg)

    @staticmethod
    def default_map():
        map_path = os.path.join(os.path.dirname(__file__), 'maps/default.py')
        return map_path

    @staticmethod
    def default_settings():
        return default_settings

    def game(self, record_turns=False, unit_testing=False):
        return game.Game(self._players, record_turns=record_turns,
                         unit_testing=unit_testing)

    def run(self):
        scores = []
        print(self.options.n_of_games)
        for i in xrange(self.options.n_of_games):
            # A sequential, deterministic seed is used for each match that can
            # be overridden by user provided ones.
            match_seed = str(self.options.game_seed) + '-' + str(i)
            if self.options.match_seeds and i < len(self.options.match_seeds):
                match_seed = self.options.match_seeds[i]
            result = self.play()
            scores.append(result)
            if self.options.quiet >= 3 and not self.options.print_info:
                self.unmute_all()
            print '{0} - seed: {1}'.format(result, match_seed)
        return scores

    def play(self):
        if self.options.play_in_thread:
            g = game.ThreadedGame(self._players,
                                  print_info=self.options.print_info,
                                  record_actions=self.options.print_info,
                                  record_history=True,
                                  seed=self.options.match_seeds,
                                  quiet=self.options.quiet,
                                  delta_callback=self._delta_callback,
                                  symmetric=self.options.symmetric)
        else:
            g = game.Game(self._players,
                          print_info=self.options.print_info,
                          record_actions=self.options.print_info,
                          record_history=True,
                          seed=self.options.match_seeds,
                          quiet=self.options.quiet,
                          delta_callback=self._delta_callback,
                          symmetric=self.options.symmetric)

        if self.options.print_info and not self.options.curses:
            # only import render if we need to render the game;
            # this way, people who don't have tkinter can still
            # run headless
            from rgkit.render import render

        g.run_all_turns()
        self.game = g

        if self.options.print_info and not self.options.curses:
            #print "rendering %s animations" % ("with"
            #                               if animate_render else "without")
            render.Render(g, self.options.animate_render, names=self._names)

        # TODO: Displaying multiple games using curses is still a little bit
        # buggy but at least it doesn't completely screw up the state of the
        # terminal anymore.  The plan is to show each game sequentially.
        # Concurrency in run.py needs some more work before the bugs can be
        # fixed. Need to make sure nothing is printing when curses is running.
        if self.options.print_info and self.options.curses:
            from rgkit import rgcurses
            rgc = rgcurses.RGCurses(g, self._names)
            if self._rgcurses_lock:
                self._rgcurses_lock.acquire()
            rgc.run()
            if self._rgcurses_lock:
                self._rgcurses_lock.release()

        return g.get_scores()

    @staticmethod
    def is_multiprocessing_supported():
        is_multiprocessing_supported = True
        try:
            imp.find_module('multiprocessing')
        except ImportError:
            # the OS does not support it. See http://bugs.python.org/issue3770
            is_multiprocessing_supported = False

        return is_multiprocessing_supported


def _task(arg):
    return Runner.from_command_line_args(arg).run()


def run_concurrently(args):
    import multiprocessing
    num_cpu = multiprocessing.cpu_count()
    (games_per_cpu, remainder) = divmod(args.count, num_cpu)
    data = []
    for i in xrange(num_cpu):
        copy_args = copy.deepcopy(args)

        if i == 0:
            copy_args.count = games_per_cpu + remainder
        else:
            copy_args.count = games_per_cpu

        data.append(copy_args)

    pool = multiprocessing.Pool(num_cpu)
    results = pool.map(_task, data, 1)
    return [score for scores in results for score in scores]


def arg_parser():
    parser = argparse.ArgumentParser(description=
                                     "Robot game execution script.",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument("player1",
                        help="File containing first robot class definition.")
    parser.add_argument("player2",
                        help="File containing second robot class definition.")
    defalut_map = pkg_resources.resource_filename('rgkit', 'maps/default.py')
    parser.add_argument("-m", "--map",
                        help="User-specified map file.",
                        default=defalut_map)
    parser.add_argument("-c", "--count", type=int,
                        default=1,
                        help="Game count, default: 1, multithreading if >1")
    parser.add_argument("-A", "--animate", action="store_true",
                        default=False,
                        help="Enable animations in rendering.")
    parser.add_argument("-q", "--quiet", action="count",
                        help="Quiet execution.\n\
    -q : suppresses bot stdout\n\
    -qq: suppresses bot stdout and stderr\n\
    -qqq: supresses all rgkit and bot output")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-H", "--headless", action="store_true",
                       default=False,
                       help="Disable rendering game output.")
    group.add_argument("-T", "--play-in-thread", action="store_true",
                       default=False,
                       help="Separate GUI thread from robot move calculations."
                       )
    group.add_argument("-C", "--curses", action="store_true",
                       default=False,
                       help="Display game in command line using curses.")
    parser.add_argument("--game-seed",
                        default=random.randint(0, default_settings.max_seed),
                        help="Appended with game countfor per-match seeds.")
    parser.add_argument("--match-seeds", nargs='*',
                        help="Used for random seed of the first matches"
                        + " in order.")
    parser.add_argument("-s", "--symmetric", action="store_true",
                        default=False,
                        help="Bots spawn symmetrically.")
    parser.add_argument("-M", "--heatmap", action="store_true",
                        default=False,
                        help="Print heatmap after playing a number of games.")

    return parser


def mute_all():
    sys.stdout = game.NullDevice()
    sys.stderr = game.NullDevice()


def unmute_all():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def print_score_grid(scores, player1, player2, size):
    max_score = 50

    def to_grid(n):
        return int(round(float(n) / max_score * (size - 1)))

    def print_heat(n):
        if n > 9:
            sys.stdout.write(" +")
        else:
            sys.stdout.write(" " + str(n))

    grid = [[0 for c in xrange(size)] for r in xrange(size)]

    for s1, s2 in scores:
        grid[to_grid(s1)][to_grid(s2)] += 1

    p1won = sum(p1 > p2 for p1, p2 in scores)
    str1 = player1 + " : " + str(p1won)
    if len(str1) + 2 <= 2 * size - len(str1):
        str1 = " " + str1 + " "
        print "*" + str1 + "-" * (2 * size - len(str1)) + "*"
    else:
        print str1
        print "*" + "-" * (2 * size) + "*"

    for r in xrange(size - 1, -1, -1):
        sys.stdout.write("|")
        for c in xrange(size):
            if grid[r][c] == 0:
                if r == c:
                    sys.stdout.write(". ")
                else:
                    sys.stdout.write("  ")
            else:
                print_heat(grid[r][c])
        sys.stdout.write("|\n")

    p2won = sum(p2 > p1 for p1, p2 in scores)
    str2 = player2 + " : " + str(p2won)
    if len(str2) + 2 <= 2 * size - len(str2):
        str2 = " " + str2 + " "
        print "*" + "-" * (2 * size - len(str2)) + str2 + "*"
    else:
        print "*" + "-" * (2 * size) + "*"
        print str2


def main(robot1, robot2):
    #args = arg_parser().parse_args()
    #args = [robot1, robot2]
    #if args.quiet >= 3:
    #    mute_all()

    #print('Game seed: {0}'.format(args.game_seed))

    #if Runner.is_multiprocessing_supported() and args.count > 1:
    #    runner = run_concurrently
    # else:
        #runner = lambda _args: Runner.from_command_line_args(_args).run()
    runner = Runner(player1_file=robot1, player2_file=robot2).run()
    print runner.result
    #scores = runner(args)

    #if args.count > 1:
    #    p1won = sum(p1 > p2 for p1, p2 in scores)
    #    p2won = sum(p2 > p1 for p1, p2 in scores)
    #    if args.heatmap:
    #        print_score_grid(scores, args.player1, args.player2, 26)
    #    print [p1won, p2won, args.count - p1won - p2won]


if __name__ == '__main__':
    main()
