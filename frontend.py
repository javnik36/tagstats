from bottle import *
# from bottle.ext import sqlite as sql
# from bottle_sqlite import SQLitePlugin
import sqlite3 as sql
import jinja2 as j2
TEMPLATE_PATH[:] = ["templates"]

# first_db = SQLitePlugin(dbfile='db/dev/tagstats1.db', keyword='tagg')
# install(first_db)


@route('/')
@jinja2_view("base.html")
def startpage():
    # return {"update": "NOW!!!"}
    return {"content": '''<section class="row"><div class="col s12
    b"><h5>Welcome on site TagStats!</h5><br>Site, where you can easily look
    how the OpenStreetMap tags usage changes in
    time.<br><br><br><br><br><h4>Bla, bla, bla...<a href="./tags.html">SHOW
    ME CHARTS!</a></h4></div></section>''', "update": "Now!"}


@route('/materialize/<filename:path>')
def statics(filename):
    return static_file(filename, root='web/materialize')


@route('/tags')
@jinja2_view("tags_list_templ_NEW.html")
def tag_list():  # (tagg) same error without...initializng plugin
    # rowy = tagg.execute(
    #     'SELECT "name" FROM "keys" WHERE name="area:highway"').fetchone()
    connection = sql.connect('db/dev/tagstats1.db')
    c = connection.cursor()
    rowy = c.execute(
        'SELECT DISTINCT "name" FROM "keys" ORDER BY "name" ASC').fetchall()
    connection.close()
    if rowy != []:
        return {"tags": rowy}
    else:
        return HTTPError(404)


def make_main_graph(feed):
    from datetime import date
    from nvd3 import lineChart
    import time

    alles = []
    n = []
    w = []
    r = []
    u = []
    d = []

    for i in feed:
        alles.append(i[0])
        n.append(i[1])
        w.append(i[2])
        r.append(i[3])
        u.append(i[4])
        d_n = str(i[5])
        d_r = int(d_n[:4])
        d_m = int(d_n[4:6])
        d_d = int(d_n[6:])
        data_obj = date(d_r, d_m, d_d)
        new_d = time.mktime(data_obj.timetuple()) * 1000
        d.append(new_d)

    chart = lineChart(
        height="400", width="900", x_is_date=True, x_axis_format="%d-%m", use_interactive_guideline=True)
    chart.add_serie(x=d, y=alles, name="All")
    chart.add_serie(x=d, y=n, name="Nodes")
    chart.add_serie(x=d, y=w, name="Ways")
    chart.add_serie(x=d, y=r, name="Relations")
    chart.add_serie(x=d, y=u, name="Users used")

    chart.buildcontent()
    return chart.htmlcontent


def make_val_graphs(name, val_list):
    from datetime import date
    from nvd3 import lineChart
    import time

    connection = sql.connect("db/dev/tagstats_values1.db")
    c = connection.cursor()
    # distinct = '''SELECT DISTINCT "value" FROM "values" WHERE '''
    # dist_db = c.execute(distinct.format(ch_name)).fetchall()
    value_content = []

    o = 1
    for i in val_list:
        # clear tables
        alles = []
        n = []
        w = []
        r = []
        d = []

        vals = '''SELECT alles,nodes,ways,relations,data FROM "values" WHERE key="{0}" AND value="{1}" ORDER BY data ASC'''

        value_name = i[0]
        val_db = c.execute(vals.format(name, value_name)).fetchall()

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
        # chart_name = ch_name + "-" + value_name
        ch = "Chart_No" + str(o)

        chart = lineChart(
            name=ch, height="400", width="800", x_is_date=True, x_axis_format="%d-%m", use_interactive_guideline=True)
        chart.add_serie(x=d, y=alles, name="All")
        chart.add_serie(x=d, y=n, name="Nodes")
        chart.add_serie(x=d, y=w, name="Ways")
        chart.add_serie(x=d, y=r, name="Relations")

        # if tofile == True:
        #     out_f = open("{0}.html".format(chart_name), 'w')
        #     chart.buildhtml()
        #     out_f.write(chart.htmlcontent)
        #     out_f.close()
        # else:
        # val_div = chart.buildcontainer()
        # val_js = chart.buildjschart()
        chart.buildcontent()
        val_data = chart.htmlcontent
        sm_dict = {"name": value_name, "graph": val_data}
        value_content.append(sm_dict)
        o += 1

    connection.close()
    return value_content


@route('/tags/<tag>')
@jinja2_view("tag_template_NEW.html")
def tag_data(tag):
    connection = sql.connect('db/dev/tagstats1.db')
    c = connection.cursor()
    rowy = c.execute(
        'SELECT alles,nodes,ways,relations,used_by,data FROM keys WHERE name="{0}" ORDER BY data ASC'.format(tag)).fetchall()
    connection.close()

    if rowy == []:
        return HTTPError(503)

    connection = sql.connect('db/dev/tagstats_values1.db')
    c = connection.cursor()
    val_rows = c.execute(
        'SELECT DISTINCT value FROM "values" WHERE key="{0}"'.format(tag)).fetchall()
    connection.close()

    content = make_main_graph(rowy)

    if val_rows == []:
        Vcontent = None
        vIndex = "false"
    else:
        Vcontent = make_val_graphs(tag, val_rows)
        vIndex = "true"

    return {"tag_name": tag, "graph": content, "is_val_index": vIndex, "values": Vcontent}

run(host='localhost', port=8080, debug=True)  # , reloader=True)
