# SSM(siteSpeedMessage) = Agent 정보(environment) + 응답 받은 측정 메트릭(metrics)
 
from glob import glob
from pprint import pprint
from shutil import copyfile
from datetime import datetime
from ua_parser import user_agent_parser
from pytz import timezone
import xmltodict
import json
import gzip
import uuid
import os, sys
 
 
# Define Functions
# cur_date2 : Date using for docker cp (UTC)
def make_utc_date():
    cur_date2 = datetime.utcnow()
    cur_date2 = cur_date2.strftime('%y/%m/%d/')
     
    return cur_date2
     
def get_test_url_list(test_dir):
    test_url_list = []
    with open('{}urls2.txt' .format(test_dir)) as f:
        for line in f:
            line = line.replace('\n', '')
            test_url_list.append(line)
            test_url_list = sorted(test_url_list)
    return test_url_list
 
def get_file_list(result_dir, file_format):
    file_list = []
    for file in glob('{}*.{}' .format(result_dir, file_format)):
        file_list.append(file)
     
    file_list = sorted(file_list)
    return file_list

# xml -> json
def xml_to_json(test_url_list, xml_file_list, result_dir):
    for num in range(len(test_url_list)):
        with open(xml_file_list[num]) as f1:
            xml_string = f1.read()
         
        json_string = json.dumps(xmltodict.parse(xml_string), indent=4)
        # Save json file : /home/sasuh/test/result/1912261025/www.gmarket.co.kr.json
        with open('{}.json' .format(result_dir + test_url_list[num]), 'w') as f2:
            f2.write(json_string)
                         
# docker file cp
def cp_file(xml_file_list, result_dir, cur_date2, test_url_list):
    for i in range(len(xml_file_list)):
        test_id = xml_file_list[i].split('_')
        test_id = test_id[-2] + '/' + test_id[-1]
        test_id = test_id.replace('.xml', '/')
        copy_file = '1_devtools_requests.json.gz'
        copy_dir1 = '/home/sasuh/docker_files/volumes/docker_results/_data/'
        copy_dir2 = cur_date2 + test_id
         
        # server:/var/www/html/results/20/02/02/test_id/1_devtools_requests
        copy_dir = copy_dir1 + copy_dir2 + copy_file
        os.system('cp {} {}' .format(copy_dir, result_dir))
        os.system('mv {} {}' .format(result_dir + copy_file, result_dir + test_url_list[i] + '.' + copy_file))
 
# upper -> lower
def upper_to_lower(all_dict, test_name, value):
    if test_name == 'TTFB':
        test_name = test_name.lower()
 
    else:
        for num in range(len(test_name)):
            if test_name[num].isupper() == 1:
                test_name = test_name.replace(test_name[num],'_' + test_name[num].lower())
                test_name = test_name.replace('::', '')
                test_name = test_name.replace('__', '_')
                 
        all_dict[test_name] = value
    return all_dict
 
# Create site speed msg
def make_ssm(gz_file_list, json_file_list, test_url_list, 
result_dir):
    for i in range(len(gz_file_list)):
        # 1. jsonData1 = 1_devtools_requests.json.gz
        with gzip.open(gz_file_list[i], 'rb')  as f:
            content = f.read()
 
        content = content.decode('utf-8')
        jsonData1 = json.loads(content)
 
        # 2. jsonData2 = www.auction.co.kr.json
        with open(json_file_list[i]) as f:
            jsonData2 = json.load(f)
 
        requestsData = jsonData1['requests'][0]
 
        ip = requestsData['ip_addr']
 
        testUrl = requestsData['full_url']
        testUrl = testUrl.replace('http://', '')
 
        for a in requestsData['headers']['request']:
            if (a.find('User-Agent') == 0):
                ua = a.split(':')[-1].strip()
        parsed_ua = user_agent_parser.Parse(ua)
         
        data = jsonData2['response']['data']
        fv = data['median']['firstView']
                 
        deviceType = int(data['mobile'])        # deviceType = 0 (Web), deviceType = 1(Mobile)
        if deviceType == 0:
            deviceType = 'Mobile'
        else:
            deviceType = 'Web'
                 
        connectType = data['connectivity']
                 
        timeStamp = fv['date']
        timeStamp = float(timeStamp)    # 1573005503.6636 -> 2019-11-06 10:58:23
         
        # result_file_dir
        UTC_date = datetime.fromtimezone(timeStamp, timezone('UTC')).replace(microsecond=0).isoformat()
         
        # local time (for kibana)
        KST_date = datetime.fromtimezone(timeStamp, timezone('Asia/Seoul')).replace(microsecond=0).isoformat()
       
        messageId = str(uuid.uuid4())
 
        testUrl2 = testUrl.split('.')           # ['www', 'auction', 'co', 'kr/']
        testUrl2 = testUrl2[1]
        serviceId = '{}:{}' .format(testUrl2, uuid.uuid4())
 
        all_dict = dict()
        #all_dict = {'service_id' : serviceId, 'message_id' : messageId, 'test_url' : testUrl, 'device_type' : deviceType, 'connect_type' : connectType, 'ip' : ip, 'date' : date, 'time_stamp' : timeStamp, 'user_agent' : userAgent}
        all_dict = {'service_id' : serviceId, 'message_id' : messageId, 'test_url' : testUrl, 'device_type' : deviceType, 'connect_type' : connectType, 'ip' : ip, 'utc_date' : UTC_date, 'kat_date' : KST_date, 'time_stamp' : timeStamp}
        
        # Data parsing
        # 1. upper -> lower
        metricList = ['TTFB', 'cached','render', 'requests', 'server_rtt', 'responses_200', 'responses_404', 'responses_other', 'result', 'bytesIn', 'bytesOut',
        'loadTime', 'domTime', 'effectiveBps', 'requestsDoc', 'visualComplete', 'firstPaint', 'firstContentfulPaint', 'firstMeaningfulPaint', 'fullyLoaded']
 
        for metric in metricList:
            if metric in fv.keys():
                value = int(float(fv[metric]))
                upper_to_lower(all_dict, metric, value)
 
        # 2. chromeUserTiming -> cut_ && upper -> lower
        for key in fv.keys():
            if 'chromeUserTiming.' in key:
                value = int(float(fv[key]))
                key = key.replace('chromeUserTiming.', 'cut_')
                upper_to_lower(all_dict, key, value)
 
        errorCode = int(requestsData['responseCode'])
        errorMessage = requestsData['headers']['response'][0]
 
        error_dict = {'code' : errorCode, 'message' : errorMessage}
        
        siteSpeedMessage = {'api_version' : 'v1', 'data' : all_dict, 'error' : error_dict, 'geo_ip' : geo_ip, 'userAgent' : parsed_ua}
 
        # /home/sasuh/test/result/1912261025/www.gmarket.co.kr.SSM.json
        with open('{}.SSM.json' .format(result_dir + test_url_list[i]), 'w', encoding='utf-8') as makeFile:
            json.dump(siteSpeedMessage, makeFile, indent='\t', sort_keys = True)
            
# Execute All Functions
if __name__ == "__main__":
    # cur_date1, cur_date2
    cur_date1 = sys.argv[1]     # sys.argv[0] = python_file_name
     
    cur_date2 = make_utc_date()
    
    result_dir = '/home/sasuh/wpt_result/{}/' .format(cur_date1)
 
    test_dir = '/home/sasuh/wpt_test/'
 
    # 2. Get test_url List
    test_url_list = get_test_url_list(test_dir)
 
    # 3. Get xml_file_list
    xml_file_list = get_file_list(result_dir, 'xml')
 
    # 4. xml -> json
    xml_to_json(test_url_list, xml_file_list, result_dir)
 
    # 5. docker cp
    cp_file(xml_file_list, result_dir, cur_date2, test_url_list)
 
    # 6. gz_file_list & json_file_list (using for file parsing)
    gz_file_list = get_file_list(result_dir, 'gz')
    json_file_list = get_file_list(result_dir, 'json')
 
    # 7. Site Speed Message
    make_ssm(gz_file_list, json_file_list, test_url_list, result_dir)
