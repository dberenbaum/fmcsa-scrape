import argparse
import itertools
import time

import scraper


def main():

    parser = argparse.ArgumentParser(description="""Get data for motor carriers
                                    covered by given insurers from Federal Motor
                                    Carrier Safety Adminstration.""")
    parser.add_argument("--state", "-s", required=True, help="""State in which
                        to search""")
    parser.add_argument("--infile", "-i", required=True, help="""Path to text
                        file containing pv_inser_id for each insurer of interest
                        (one per line)""")
    parser.add_argument("--outfile", "-o", required=True, help="""Path to file
                        for writing results.""")
    parser.add_argument("--start", default=1, type=int, help="""Number of search
                        result at which to begin.""")
    parser.add_argument("--step", default=1000, help="""Number of search results
                        to process at a time.""")
    parser.add_argument("--mode", default="w", choices=["w", "a"],
                        help="""File mode.""")
    parser.add_argument("--sleep", default="600", type=int, help="""Number of
                        seconds to sleep between batches of requests.""")

    args = parser.parse_args()

    insurers = []
    with open(args.infile) as f:
        insurers = [line.strip() for line in f.readlines()]

    state = args.state
    start = args.start
    step = args.step
    mode = args.mode
    sleep = args.sleep

    outfile = "%s_carriers.csv" % state
    if args.outfile:
        outfile = args.outfile

    for start in itertools.count(start=start, step=step):

        stop = start + step - 1

        t = time.strftime("%H:%M", time.localtime())
        print("%s Starting next %d records" % (t, step))

        query_dict = {"s_state": "%sUS" % state, "p_begin": start,
                      "p_end": stop}

        carriers = scraper.get_carriers(query_dict)

        if carriers:
            filtered = scraper.insurer_filter(carriers, insurers)

            if filtered:
                scraper.write_carriers(filtered, outfile=outfile, mode=mode)

        t = time.strftime("%H:%M", time.localtime())
        print("%s Scraped records %d through %d" % (t, start,
                                                    start + len(carriers) - 1))

        time.sleep(sleep)

        if len(carriers) < step:
            break


if __name__ == "__main__":
    main()
