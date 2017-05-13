#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading, os
import re
import requests

class AUD2RMB:
    _lock = threading.RLock()
    def __init__(self, id, title, feasible = True):
        self.id = id
        self.title = title
        self.feasible = feasible
        self.category = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        try:
            with AUD2RMB._lock:
                # refered from https://www.zhihu.com/question/52679464
                url = 'http://www.boc.cn/sourcedb/whpj/'
                response = requests.get(url)
                content = response.content.decode('utf-8')
                index = content.index(u'<td>澳大利亚元</td>')
                result = content[index:index + 300]
                result_list = re.findall('<td>(.*?)</td>', result)
                return str(float(result_list[3]) / 100)
        except Exception as e:
            return str(e)