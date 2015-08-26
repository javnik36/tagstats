import jinja2 as j2
from db_app import *
from time import localtime, strftime
# values = [value1, value2...]
# value1 = {name: ..., graph: ...}
# values = [{name:, graph: }, ...]


def make_graphs(tag_name, values=False, tofile=False):
    import sqlite3 as sql
    # import matplotlib.pyplot as p
    # from bokeh.plotting import figure, output_file, show
    from datetime import date
    from nvd3 import lineChart
    import time

    ch_name = change_name(tag_name)

    connection = sql.connect("db\\tagstats.db")
    c = connection.cursor()

    base = '''SELECT alles,nodes,ways,relations,used_by,data FROM "{0}" ORDER BY data ASC'''

    key_db = c.execute(base.format(ch_name)).fetchall()
    # list of tuple [(1,2,3), (1,2,3) ]
    alles = []
    n = []
    w = []
    r = []
    u = []
    d = []

    value_list = []

    for i in key_db:
        alles.append(i[0])
        n.append(i[1])
        w.append(i[2])
        r.append(i[3])
        u.append(i[4])
        d_n = str(i[5])
        d_r = int(d_n[:4])
        d_m = int(d_n[4:6])
        d_d = int(d_n[6:])
        # d_str = "{0}-{1}-{2}".format(d_n[:4], d_n[4:6], d_n[6:])
        # d.append(d_str)
        # print(d_str)
        data_obj = date(d_r, d_m, d_d)
        new_d = time.mktime(data_obj.timetuple()) * 1000
        d.append(new_d)
        # d.append(i[5])
        # d.append("{0},{1},{2}".format(d_n[:4], d_n[4:6], d_n[6:]))

    chart = lineChart(
        name=ch_name, height="400", width="800", x_is_date=True, x_axis_format="%d-%m", use_interactive_guideline=True)
    chart.add_serie(x=d, y=alles, name="All")
    chart.add_serie(x=d, y=n, name="Nodes")
    chart.add_serie(x=d, y=w, name="Ways")
    chart.add_serie(x=d, y=r, name="Relations")
    chart.add_serie(x=d, y=u, name="Users used")
    # chart.create_x_axis(
    #     name=x_Axis, label="Data", date=True, format="%Y%m%d")

    if tofile == True:
        out_f = open("{0}.html".format(ch_name), 'w')
        chart.buildhtml()
        out_f.write(chart.htmlcontent)
        out_f.close()
    else:
        chart.buildcontent()
        tag_data = chart.htmlcontent

        # make_graphs("area:highway")
    connection.close()
    if values == True:
        # make_graphs("area:highway",True)
        connection = sql.connect("db\\tagstats_values.db")
        c = connection.cursor()
        distinct = '''SELECT DISTINCT value FROM "{0}"'''
        dist_db = c.execute(distinct.format(ch_name)).fetchall()

        for i in dist_db:
            # clear tables
            alles.clear()
            n.clear()
            w.clear()
            r.clear()
            d.clear()

            vals = '''SELECT alles,nodes,ways,relations,data FROM "{0}" WHERE value="{1}" ORDER BY data ASC'''

            value_name = i[0]
            val_db = c.execute(vals.format(ch_name, value_name)).fetchall()

            for i in val_db:
                alles.append(i[0])
                n.append(i[1])
                w.append(i[2])
                r.append(i[3])
                d_n = str(i[4])
                d_r = int(d_n[:4])
                d_m = int(d_n[4:6])
                d_d = int(d_n[6:])
                data_obj = date(d_r, d_m, d_d)
                new_d = time.mktime(data_obj.timetuple()) * 1000
                d.append(new_d)

            # change this shit...it will makes problems with file names
            chart_name = ch_name + "-" + value_name

            chart = lineChart(
                name=chart_name, height="400", width="800", x_is_date=True, x_axis_format="%d-%m", use_interactive_guideline=True)
            chart.add_serie(x=d, y=alles, name="All")
            chart.add_serie(x=d, y=n, name="Nodes")
            chart.add_serie(x=d, y=w, name="Ways")
            chart.add_serie(x=d, y=r, name="Relations")

            if tofile == True:
                out_f = open("{0}.html".format(chart_name), 'w')
                chart.buildhtml()
                out_f.write(chart.htmlcontent)
                out_f.close()
            else:
                # val_div = chart.buildcontainer()
                # val_js = chart.buildjschart()
                chart.buildcontent()
                val_data = chart.htmlcontent
                sm_dict = {"name": value_name, "graph": val_data}
                value_list.append(sm_dict)

        connection.close()
    # print(values)
    # print(value_list)
    return (tag_name, values, tag_data, value_list, ch_name)

pl = j2.PackageLoader("web_util", 'templates')
envi = j2.Environment(loader=pl)


def make_tag_html(tag_name, values=False):
    try:
        content = make_graphs(tag_name, values)
    except:
        print("TAG {0} NOT FOUND!".format(tag_name))
        return None

    template = envi.get_template("tag_template.html")

    u_tag = strftime("%d %b %Y %H:%M:%S", localtime())

    made_templ = template.render({'tag_name': content[0], 'is_val_index': content[
        1], 'graph': content[2], 'values': content[3], 'update': u_tag})

    with open("web/tags/{0}.html".format(content[-1]), 'w', encoding='utf-8') as h:
        h.write(made_templ)


def make_tags_list_html():
    # import sqlite3 as sql
    all_tags = key_only + key_dont
    all_tags.sort()
    to_html = []
    for i in all_tags:
        ch_name = change_name(i)
        if ch_name == i:
            to_html.append((i, i))
        else:
            to_html.append((ch_name, i))

    u_tag = strftime("%d %b %Y %H:%M:%S", localtime())
    template = envi.get_template("tags_list_templ.html")
    made_templ = template.render({"tags": to_html, "update": u_tag})

    with open("web/tags.html", 'w', encoding='utf-8') as h:
        h.write(made_templ)
