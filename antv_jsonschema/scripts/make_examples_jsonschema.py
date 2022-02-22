import requests
from lxml import etree
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Any
import json
import logging
import datetime
import os
import logging.config
import re

LOG_DIR = 'var/log'

LOG_FILE = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"

LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
            'standard': {
                'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",  
            },

            "default": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": os.path.join(LOG_DIR, LOG_FILE),
                'mode': 'w',
                "maxBytes": 1024*1024*5,  # 5 MB
                "backupCount": 20,
                "encoding": "utf8"
            },
        },
        "root": {
            'handlers': ['default'],
            'level': "DEBUG",
            'propagate': False
        }
    }

logging.config.dictConfig(LOGGING)

class AttrProps(BaseModel):

    required: bool = False
    type: str
    default: Optional[Any]
    enum: Optional[list]
    title: str
    description: Optional[str]
    examples: Optional[list]
    items: Optional[dict]


def _parase_props(ele, title:str) -> dict:
    """解析props"""
    
    props = {
        'title': title,
        'default': None,
        'required': False,
        'type': 'string'
    }

    base = ele.xpath('./following-sibling::div[1]/description')

    desc = ele.xpath('./following-sibling::p[1]/text()')

    if not base:
        props['required'] = False
    else:
        base = base[0]

        # 是否必填
        required = base.xpath('./strong/text()')
        props['required'] = True if required and required[0] == 'required' else False

        # 数据类型
        data_type = base.xpath('./em/text()')[0]
        

        props['type'] = data_type if data_type else 'string'

        # 数组
        if '[]' in props['type']:
            props['type'] = 'array'
            data_type = data_type[0]
            if 'number' in data_type:
                props['items'] = {'type': 'number'}
            elif 'string' in data_type:
                props['items'] = {'type': 'string'}
            else:
                props['items'] = {'type': 'string'}
        elif 'array object' in props['type']:
            props['type'] = 'array'
            props['items'] = {'type': 'object'}
        elif 'array' in props['type']:
            props['type'] = 'array'
            props['items'] = {'type': 'string'}
        # 枚举
        elif '|' in props['type']:
            props['type'] = 'string'
            logging.debug(f'含 "|" | {title} | {data_type}')
            # 正则提取枚举项，排除Function
            _c = re.compile('\w+')
            data_type = ''.join(data_type.split())
            _match = _c.findall(data_type)
            enums = list(set(_match))
            if 'StyleAttr' in enums:
                enums.remove('StyleAttr')
            if 'Function' in enums:
                enums.remove('Function')
            props['enum'] = enums

        elif 'any' in props['type']:
            return None
        
        # 默认值
        default = base.xpath('./em[contains(text(), "default")]/following-sibling::code[1]/text()')

        props['default'] = default[0] if default else None

    if desc:
        props['description'] = desc[0]

    return props
    

def make_line_config(filepath):
    """生成line chart配置"""

    _jsonschema = {
        'type': 'object',
        'properties': {},
        'required': []
    }

    # 读取本地化的api文档
    # filepath = 'antv_jsonschema/resources/g2plot.antv.vision/zh/docs/api/plots/line.html'
    with open(filepath, 'r') as f:
        html = etree.HTML(f.read())

    # 关于某个图表的配置项，这里以折线图为例
    content = html.xpath('//div[contains(@class, "markdown-module--content--1HSJ5")]/div')
    if not content:
        return
    content = content[0]

    # 配置属性
    attr_title_h4 = content.xpath('./h4')
    for item in attr_title_h4:
        # 属性名称
        name = item.xpath('./text()')
        if not name:
            continue
        name = name[0]

        # 辅助线相关的配置项，不能完全借助jsonschema直接配置成表格，需要定制化，暂不考虑
        if '💠' in name or 'Annotation' in name:
            continue
        
        # 解析当前属性的，必填、默认值、数据类型等
        attr_props = _parase_props(item, name)
        if attr_props:
            _jsonschema['properties'][name] = attr_props
        # break

    _jsonschema['required'] = [k for k, v in _jsonschema['properties'].items() if v['required'] is True]

    filename = filepath.split(os.sep)[-1].replace('.html', '')
    with open(f'var/tmp/schema/{filename}.json', 'w') as f:
        f.write(json.dumps(_jsonschema))
    

# make_line_config()

if __name__ == '__main__':
    
    api_dir = 'antv_jsonschema/resources/g2plot.antv.vision/zh/docs/api/plots'
    for root, _dir, _path in os.walk(api_dir):
        for filename in _path:
            if '.html' not in filename:
                continue
            filepath = os.path.join(root, filename)
            try:
                make_line_config(filepath)
            except Exception as e:
                pass