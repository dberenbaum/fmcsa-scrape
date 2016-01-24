import csv
import os
import re
from bs4 import BeautifulSoup
from urllib import parse, request


search_url = "http://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?%s"
insurance_url = "http://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_activeinsurance?%s"
tbl_fields = ["usdot_number", "prefix", "docket_number", "legal_name",
              "dba_name", "city", "state"]


def get_carriers(query_dict):
    """Perform search and return list of carriers."""

    carriers = []

    # Get html.
    query_string = parse.urlencode(query_dict)
    response = request.urlopen(search_url % query_string)

    # Make list of dicts for each carrier id (pv_apcant_id).
    soup = BeautifulSoup(response, "html.parser")
    for apcant_id in soup.find_all("input", attrs={"name": "pv_apcant_id"}):
        carriers.append({"pv_apcant_id": apcant_id.attrs["value"]})

    # Add all info from html table to each carrier.
    for field in tbl_fields:
        for car_ix, tag in enumerate(soup.find_all("td",
                                                     attrs={"headers": field})):
            carriers[car_ix][field] = tag.string

    return carriers


def insurer_filter(carriers, insurers):
    """Filter carriers by insurer pv_inser_id."""

    ins_carriers = {insurer: [] for insurer in insurers}

    for carrier in carriers:

        query_string = parse.urlencode({"pv_apcant_id": carrier["pv_apcant_id"]})
        response = request.urlopen(insurance_url % query_string)
        soup = BeautifulSoup(response, "html.parser")

        for ins_id in insurers:
            if soup.find_all("a", href=re.compile("pv_inser_id=%s" % ins_id)):
                ins_carriers[ins_id].append(carrier)

    return ins_carriers


def write_carriers(ins_carriers, outdir=os.getcwd()):
    """Write list of carriers to csv for each insurer."""

    for ins_id, carriers in ins_carriers.items():

        with open("%s.csv" % ins_id, "w") as outfile:
            writer = csv.DictWriter(outfile, tbl_fields)
            writer.writeheader()
            for carr_dict in carriers:
                writer.writerow({k: v for k, v in carr_dict.items() if k in
                                 tbl_fields})
