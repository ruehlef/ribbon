r"""
Randomly add bands to a knot or link
"""
import snappy
import numpy as np
import logging
import argparse
import ribbon.rw
import ribbon.visualizer as visualizer

def init_logger(log_level):
    logger = logging.getLogger('RandomWalker')
    if not logger.hasHandlers():  # don't load multiple loggers into sage
        logger_handler = logging.StreamHandler()
        logger_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(logger_handler)
    logger.setLevel(log_level)
    return logger


def parse_string_array(links):
    my_links, my_link_bws = [], []
    for x in links:
        try:
            tmp_link = eval(x)
            if isinstance(tmp_link, list):
                if isinstance(tmp_link[0], int):  # was a braid word
                    my_link_bws += [tmp_link]
                else:  # was a pd code
                    my_links += [tmp_link]
            else:  # was a link name
                my_links += [x]
        except Exception:  # was a link name
            my_links += [x]
    return my_links, my_link_bws


if __name__ == "__main__":
    example_usage = '''Example:
    Find a band of link K6a3 (Stevedore)        : random_walker --links 'K6a3' --verbose 1
    Specify some upper bounds                   : random_walker --links 'K6a3' --max-bands 5 --max-size 20 --max-steps 100
    Tries each knot 10 times                    : random_walker --links 'K6a3' --max-tries 10
    Check sliceness obstructions for added bands: random_walker --links 'K6a3' --use-checks
    Save bands as eps files                     : random_walker --links 'K6a3' --save-images
    Prioritize attach, do not twist, try forever: random_walker.py --links 'K6a3' --weights '[1,3,1,1,0]' --max-tries '-1'
    '''
    parser = argparse.ArgumentParser(description='Check for sliceness using a random walk to construct the bands.', epilog=example_usage, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--file', help='path to file with link info to process. One line per link (can specify name, PD code, or braid word)')
    parser.add_argument('--links', nargs='*', help='sequence of links, either given by their names or as a list of PD codes (separated by spaces)')
    parser.add_argument('--max-bands', default=5, type=int, help='max number of bands/twists/components (we use the same upper bound for all of these instead of allowing for individual upper bounds) that should be tried to add. Default: 5')
    parser.add_argument('--max-size', default=None, type=int, help='Maximum number of crossings. If ommited, num_crossings+1 will be used')
    parser.add_argument('--max-steps', default=50, type=int, help='Max number of steps for each knot. Roughly, each crossed arc corresponds to one step. Default: 50')
    parser.add_argument('--max-tries', default=1000, type=int, help='Max number of resets for each knot. Set to -1 for infinite tries. Default: 1000')
    parser.add_argument('--use-checks', default=False, action='store_true', help='if flag is set, will check for slice obstructions (signature, alexander poly, fox-milnor,...). This requires sage')
    parser.add_argument('--save-images', default=False, action='store_true', help='if flag is set, a set of images for each ribbon knot is saved (to the same directory as this script) that shows which bands were added.')
    parser.add_argument('--verbose', default=1, type=int, help='verbosity level: \'0\': only crucial info, \'1\': some info, \'2\': a lot of info, \'3\': everything (probably too much). Default: 1')
    parser.add_argument('--weights', default="[1.,17.,1.,1.,3.]", type=str, help='specify relative probabilities for sampling the actions [start, attach, over, under, twist]. Need not be normalized to 1. Default: "[1.,17.,1.,1.,3.]", i.e., which was found to work well by Bayesian optimization')
    args = parser.parse_args()

    args.max_bands = int(args.max_bands)
    args.max_steps = int(args.max_steps)
    args.max_tries = int(args.max_tries)
    args.use_checks = bool(args.use_checks)
    args.save_images = bool(args.save_images)
    args.verbose = int(args.verbose)

    # initialize logger
    if args.verbose == 0:
        log_level = logging.ERROR
    elif args.verbose == 1:
        log_level = logging.WARNING
    elif args.verbose == 2:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger = init_logger(log_level)

    # read in links
    my_links, my_link_bws = [], []
    if args.file is not None:
        logger.debug("Reading links from file {}".format(args.file))
        with open(args.file, 'r') as hnd:
            links_form_file = hnd.read()
        file_links, file_link_bws = parse_string_array(links_form_file.splitlines())
        my_links += file_links
        my_link_bws += file_link_bws

    if args.links is not None:
        cmd_line_links, cmd_line_bws = parse_string_array(args.links)
        my_links += cmd_line_links
        my_link_bws += cmd_line_bws

    for bw in my_link_bws:
        l = snappy.Link(braid_closure=bw)
        l.simplify('global')
        my_links += [l.PD_code()]

    if args.max_size is None:
        max_size = -1
        for x in my_links:
            new_crossing_num = len(snappy.Link(x))
            if new_crossing_num > max_size:
                max_size = new_crossing_num
        max_size += 1
    else:
        max_size = int(args.max_size)
    
    if args.use_checks and len(my_links) > 1:
        my_links = [my_links[0]]
        logger.warning("the flag --use-checks can only be used with a single knot. Running the RW on knot {}".format(my_links[0]))
        
    random_walker = ribbon.rw.RandomWalker(links=my_links, max_size=max_size, max_steps=args.max_steps, max_bct=args.max_bands, logger=logger, log_level=log_level, use_band_checks=args.use_checks, save_solved_knot_images=args.save_images)
    max_action_per_category = max_size + 3

    if eval(args.weights) == [1, 1, 1, 1, 1]:
        weights = None
    else:
        weights = eval(args.weights)
        weights = [float(weights[0])] * max_action_per_category + [float(weights[3]), float(weights[1]), float(weights[2])] * max_action_per_category + [float(weights[4])] * 2
    
    num_knots, success, tries, tries_per_knot = 0, 0, 0, 0
    succeeded, failed = [], []
    while True:
        tries += 1
        if tries % 10000 == 0:
            logger.info("Performed {:d} steps. Currently at knot {}/{}. Solved {}.".format(tries, num_knots, len(my_links), success))

        # random sample valid action
        if weights is None:  # specifying p in random.choice makes it a factor 5 slower, so we don't do this if we don't have to
            valid_actions = np.argwhere(random_walker.invalid_action_mask()).flatten()
            a = np.random.choice(valid_actions) if len(valid_actions) > 0 else 0
        else:
            valid_actions = np.array(random_walker.invalid_action_mask(), dtype=float)
            ws = weights * valid_actions
            ws = ws / np.sum(ws) if np.sum(ws) != 0 else [1./(4 * max_size + 2)] * (4 * max_size + 2)
            a = np.random.choice(len(valid_actions), p=ws) if valid_actions.any() else 0
        
        # perform action
        done, info = random_walker.step(a)

        if done:
            tries_per_knot += 1
            if 'unknot' in info['result']:  # solved the knot
                if args.use_checks:
                    my_links = [my_links[0]]
                    success, succeeded = 1, my_links
                    break
                succeeded += [my_links[num_knots]]
                success += 1
                num_knots += 1
                tries_per_knot = 0

        if tries_per_knot >= args.max_tries >= 0:  # args.max_tries == -1 for infinitely many tries
            logger.error("Couldn't find bands for knot {} after {} tries. Continuing with next knot.".format(random_walker.link_name, tries_per_knot))
            if args.use_checks:
                my_links = [my_links[0]]
                failed = my_links
                break
            failed += [my_links[num_knots]]
            num_knots += 1
            random_walker.num_times_solved = random_walker.max_steps_until_reset + 1  # give up on the knot and move on to next
            tries_per_knot = 0
            random_walker.reset(True)

        if random_walker.next_l >= len(random_walker.links) and not args.use_checks:
            logger.error("Finished all links")
            break

    # This is not an error, just want to print summary irrespective of verbosity
    logger.error("\n####################################################################################################")
    logger.error("Summary:")
    logger.error("Succeeded {} times for: {}".format(success, succeeded))
    logger.error("Failed    {} times for: {}".format(len(my_links) - success, failed))
    logger.error("####################################################################################################")
