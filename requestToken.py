#!/usr/bin/python3
"""
File: requestToken.py
Inputs: none
Outputs: print both access token and refresh token to screen

To use this file as a standalone script the username, password, & FMC IP
will need to be populated in the __main__ section below.
"""

# include the necessary modules
import os
import argparse
import requests


"""
function: get_token(fmcIP, path, username, password)
use: generates a list of necessary headers to be included with all 
    subsequent requests

inputs: IP of FMC, path to API, API user, API password
returns: access token, refresh token, domain uuid
"""
def get_token(fmcIP, path, username, password):
    # lets disable the certificate warning first (this is NOT advised in prod)
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # send request with a try/catch block to handle errors safely
    try:
        r = requests.post(f"https://{fmcIP}/{path}", auth=(f"{username}", 
            f"{password}"), verify=False) # always verify the SSL cert in prod!
    except requests.exceptions.HTTPError as errh:
        raise SystemExit(errh)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

    # return the request token by identifying which key:value pairs we need
    required_headers = ('X-auth-access-token', 'X-auth-refresh-token', 'DOMAIN_UUID')
    result = {key: r.headers.get(key) for key in required_headers}
    return result

"""
function: refresh_token(fmcIP, path, access token, refresh token)
use: updates the access and refresh tokens of the passed-in header bundle

inputs: IP of FMC, path to API, access token, refresh token
returns: none
"""
def refresh_token(fmcIP, path, header):
    # lets disable the certificate warning first (this is NOT advised in prod)
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # send request with a try/catch block to handle errors safely
    try:
        r = requests.post(f"https://{fmcIP}/{path}", headers=header, 
            verify=False) # always verify the SSL cert in prod!
    except requests.exceptions.HTTPError as errh:
        raise SystemExit(errh)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

     # update the request token
    header['X-auth-access-token'] = r.headers.get('X-auth-access-token')
    header['X-auth-refresh-token'] = r.headers.get('X-auth-refresh-token')

    # pass since not returning anything
    pass


# if used as a stand-alone script, run the following
if __name__ == "__main__":
    # first set up the command line arguments and parse them
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("username", type=str, help ="API username")
    parser.add_argument("password", type=str, help="password of API user")
    parser.add_argument("ip_address", type=str, help="IP of FMC")
    args = parser.parse_args()

    # set needed variables to generate a token
    u = args.username
    p = args.password
    ip = args.ip_address
    path = "/api/fmc_platform/v1/auth/generatetoken"

    # call the token generating function and populate our header
    header = get_token(ip, path, u, p)
    output_path = './outputs'
    # print the access token, refresh token, and domain uuid to the cli
    if not os.path.exists(output_path): #
        os.mkdir(output_path)
    with open('outputs/tokens.txt', 'w') as f:
        print(f"The Access Token received is: {header.get('X-auth-access-token')}", file=f)
        print(f"The Refresh Token received is: {header.get('X-auth-refresh-token')}", file=f)
        print(f"The DOMAIN_UUID is: {header.get('DOMAIN_UUID')}", file=f)
        # set the needed variables to refresh a token - only the new path, really
        path = "/api/fmc_platform/v1/auth/refreshtoken"

        # call the token refreshing function
        refresh_token(ip, path, header)
        # print the new access token and refresh token to the cli
        print(f"The refreshed Access Token received is: {header.get('X-auth-access-token')}", file=f)
        print(f"The refreshed Refresh Token received is: {header.get('X-auth-refresh-token')}", file=f)