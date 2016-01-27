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
    for tag in soup.find_all("input", attrs={"name": "pv_apcant_id"}):
        carrier = {"pv_apcant_id": tag.attrs["value"]}

        # Add all info from html table to each carrier.
        for field in tbl_fields:
            field_tag = tag.find_previous("td", attrs={"headers": field})
            carrier[field] = field_tag.string

        carriers.append(carrier)

    return carriers


def insurer_filter(carriers, insurers):
    """Filter carriers by insurer pv_inser_id, adding insurer info."""

    ins_carriers = []
    eff_dates = []
    ins_str = "|".join(insurers)
    ins_re = re.compile("pv_inser_id=(%s)" % ins_str)
    eff_re = re.compile("effective_date")

    for carrier in carriers:

        query_string = parse.urlencode({"pv_apcant_id": carrier["pv_apcant_id"]})
        response = request.urlopen(insurance_url % query_string)
        soup = BeautifulSoup(response, "html.parser")

        for tag in soup.find_all("a", attrs={"href": ins_re}):
            ins_carr = carrier.copy()
            ins_carr["insurer"] = tag.string

            eff_date_tag = tag.find_next("td", attrs={"headers": eff_re})
            ins_carr["effective_date"] = eff_date_tag.string

            ins_carriers.append(ins_carr)

    return ins_carriers


def write_carriers(carriers, outfile=os.path.join(os.getcwd(), "carriers.csv"),
                   mode="w"):
    """Write list of carriers to csv for each insurer."""

    with open(outfile, mode) as outfile:
        writer = csv.DictWriter(outfile, carriers[0].keys())
        writer.writeheader()
        writer.writerows(carriers)
