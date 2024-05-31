import json
import os
import re
import subprocess

import automatic_code_review_commons as commons


def review(config):
    rules = config['rules']
    path_source = config['path_source']
    changes = config['merge']['changes']

    comments = []

    for rule in rules:
        comments.extend(review_by_rule(path_source, rule, changes))

    return comments


def get_line_access_members(header_file):
    count = 1
    objs = []

    with open(header_file, 'r') as content:
        lines = content.readlines()

        for line in lines:
            line_tratada = line.replace(" ", "").replace("\n", "")

            if line_tratada.startswith("public") or line_tratada.startswith("private") or line_tratada.startswith("protected"):
                if line_tratada.endswith(":"):
                    objs.append({
                        'access': line.replace("\n", "").replace(":", ""),
                        'line': count
                    })

            count += 1

    return list(reversed(objs))


def get_attrs(header_file):
    # ctags
    #   Comando linux
    # --output-format=json
    #   Formato de saida em json
    # --languages=c++
    #   Linguagem c++
    # --fields=+iaSn
    #   a para Access
    #   n para Line

    data = subprocess.run(
        'ctags -R --output-format=json --languages=c++ --fields=+an --c++-kinds=+p ' + header_file,
        shell=True,
        capture_output=True,
        text=True,
    ).stdout

    objs = []
    objs_access_member = get_line_access_members(header_file)

    for data_obj in data.split('\n'):
        if data_obj == '':
            continue

        obj = json.loads(data_obj)

        if 'access' in obj and '::' not in obj['name'] and obj['kind'] != 'member':
            line = obj['line']

            for obj_access in objs_access_member:
                if line > obj_access['line']:
                    obj['access'] = obj_access['access']
                    break

        objs.append(obj)

    return objs


def verify_name_is_ignore(name, rule):
    if 'methodIgnore' not in rule:
        return False

    method_ignore = rule['methodIgnore']

    if len(method_ignore) == 0:
        return False

    if name in method_ignore:
        return True

    return False


def verify_access_filter(rule, obj):
    if 'accessFilter' not in rule:
        return True

    access_filter = rule['accessFilter']

    if len(access_filter) == 0:
        return True

    if 'access' not in obj:
        return False

    access = obj['access']

    if access not in access_filter:
        return False

    return True


def review_by_file(header_file, path_source, rule):
    comments = []
    objs = get_attrs(header_file)
    prefix = rule['prefix']

    for obj in objs:
        if not verify_access_filter(rule, obj):
            continue

        name = obj['name']

        if verify_name_is_ignore(name, rule):
            continue

        if not name.startswith(prefix):
            line = obj["line"]
            header_relative = obj["path"].replace(path_source, "")[1:]

            descr_comment = rule['comment']
            descr_comment = descr_comment.replace("${METHOD_NAME}", obj["name"])
            descr_comment = descr_comment.replace("${FILE_PATH}", header_relative)
            descr_comment = descr_comment.replace("${LINE}", str(line))

            comments.append(commons.comment_create(
                comment_id=commons.comment_generate_id(descr_comment),
                comment_path=header_relative,
                comment_description=descr_comment,
                comment_snipset=True,
                comment_end_line=line,
                comment_start_line=line,
                comment_language='c++',
            ))

    return comments


def verify_if_in_changes(changes, path):
    for change in changes:
        if change['new_path'] == path:
            return True

    return False


def review_by_rule(path_source, rule, changes):
    comments = []
    regex_file = rule['regexFile']

    for raiz, _, arquivos in os.walk(path_source):
        for arquivo in arquivos:
            header_path = os.path.join(raiz, arquivo)
            header_relative = header_path.replace(path_source, "")[1:]

            if not verify_if_in_changes(changes, header_relative):
                continue

            if re.search(regex_file, header_path):
                comments.extend(review_by_file(header_path, path_source, rule))

    return comments
