# encoding = utf-8
import json


KV_TOKEN = 'prisma_cloud_api_token'

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''


def validate_input(helper, definition):
    opt_time_unit = definition.parameters.get('time_unit', None)
    opt_interval = int(definition.parameters.get('interval', None))
    opt_time_amount = int(definition.parameters.get('time_amount', None))

    if (opt_interval < 60):
        raise ValueError(
            "Interval should greater than 60 and equal to time amount by the time unit")
    elif (opt_time_unit == "minute"):
        divide = opt_interval/60
        if (opt_time_amount == divide):
            pass
        else:
            raise ValueError(
                "Interval should greater than 60 and equal to time amount by the time unit")
    elif (opt_time_unit == "hour"):
        divide = opt_interval/3600
        if (opt_time_amount == divide):
            pass
        else:
            raise ValueError(
                "Interval should greater than 60 and equal to time amount by the time unit")
    else:
        divide = opt_interval/86400
        if (opt_time_amount == divide):
            pass
        else:
            raise ValueError(
                "Interval should greater than 60 and equal to time amount by the time unit")

    pass


def collect_events(helper, ew):
    opt_base_url = helper.get_arg('base_url')
    opt_access_key = helper.get_arg('access_key')
    opt_secret_key = helper.get_arg('secret_key')
    opt_time_amount = helper.get_arg('time_amount')
    opt_time_unit = helper.get_arg('time_unit')

    # GET EXISTING TOKEN FROM KV STORE
    token = helper.get_check_point(KV_TOKEN)

    if not token:
        # CREATE TOKEN IF ID DOES NOT EXISTS
        helper.log_info("Creating an token")
        login(helper, opt_base_url, opt_access_key, opt_secret_key)
        token = helper.get_check_point(KV_TOKEN)

    else:
        helper.log_info("Use token from KV Store and extend it.")
        status = extendToken(helper, opt_base_url, token)
        if status != 200:
            helper.log_info("Token expired, renew token.")
            login(helper, opt_base_url, opt_access_key, opt_secret_key)
            token = helper.get_check_point(KV_TOKEN)

    # GET AUDIT LOGS
    auditLogs = getAuditLogs(helper, opt_base_url,
                             opt_time_amount, opt_time_unit, token)

    for log in auditLogs:
        event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(
        ), sourcetype=helper.get_sourcetype(), data=json.dumps(log))
        ew.write_event(event)


def login(helper, opt_base_url, opt_access_key, opt_secret_key):
    url = "https://%s/login" % (opt_base_url)

    payload = json.dumps({
        "username": opt_access_key,
        "password": opt_secret_key
    })
    headers = {"content-type": "application/json; charset=UTF-8"}

    response = helper.send_http_request(url, 'POST', parameters=None, payload=payload,
                                        headers=headers, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=False)
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    token = response.json()['token']
    helper.save_check_point(KV_TOKEN, token)


def extendToken(helper, opt_base_url, token):
    # EXTEND TOKEN IF IT EXISTS
    url = "https://%s/auth_token/extend" % (opt_base_url)
    # helper.log_info("AUDITLOGS FROM EVENT ==URL: " + url)
    headers = {"x-redlock-auth": token}

    response = helper.send_http_request(url, 'GET', parameters=None, payload=None,
                                        headers=headers, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=False)

    token = response.json()['token']
    helper.save_check_point(KV_TOKEN, token)

    return response.status_code


def getAuditLogs(helper, opt_base_url, opt_time_amount, opt_time_unit, token):
    url = "https://%s/audit/redlock" % (opt_base_url)
    querystring = {"timeType": "relative",
                   "timeAmount": opt_time_amount, "timeUnit": opt_time_unit}
    headers = {"x-redlock-auth": token}
    response = helper.send_http_request(url, 'GET', parameters=querystring, payload=None,
                                        headers=headers, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=False)
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # PARSE AUDIT LOGS
    return response.json()
