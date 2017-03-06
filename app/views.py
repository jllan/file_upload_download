# coding:utf-8

from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os

#UPLOAD_FOLDER = 'app/uploads'
UPLOAD_FOLDER = '/home/jlan/uploads'
ALLOWED_EXTENSIONS = set(['txt','xls', 'xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            print(file.filename)
            # filename = secure_filename(file.filename)
            filename = file.filename
            # print(filename)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filename)
            # flash('上传成功')
            result_filename = save_another(filename)
            if result_filename:
                message = '处理成功，生成文件 "{}"，请下载'.format(result_filename)
                print(message)
            return redirect(url_for('download', filename=result_filename))
            # return redirect(url_for('upload_file', filename=filename))
    return render_template('upload.html')

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    print('download:', filename)
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'],
                               filename=filename, as_attachment=True, mimetype='application/octet-stream')



import pandas as pd
import csv

def save_another(filename):
    data = pd.read_excel(filename)
    data2 = data.ix[3:, [0, 1, 6, 7, 8, 9]]     # 只取户主编号，户主名，东南西北邻居
    data2.columns = '序号', '户主', '东', '南', '西', '北'  # 重新设置columns
    data3 = data2.dropna(how='all')             # 去除全为空的行
    data4 = data3.fillna(method='ffill')        # 用前向填充的方式填充没有户主名和户主编号的行
    data4 = data4[:-1]
    data5 = data4[data4!='道路'][data4!='沟渠'][data4!='集体地'][data4!='林带']
    data_dict = dict(zip(data5['户主'], data5['序号']))
    results_dict = {}
    for inx, row in data5.iterrows():
        nei = row[['东', '南', '西', '北']][pd.notnull(row)]    # 户主每块地的四邻
        nei_id = [str(data_dict.get(name)) for name in nei if name in data_dict]  # 户主每块地的四邻的id
        # print(nei_id)
        ids = results_dict.get(row['户主'], set())    # 用一个set()来保存四邻的id，初始为空set
        ids.update(nei_id)
        results_dict[row['户主']] = ids

    # print(results_dict)
    result_filename = filename.split('.')[0]+'_result.csv'
    with open(result_filename, 'w') as csvfile:
        fieldnames = ['户主', '四邻']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in results_dict.items():
            writer.writerow({'户主': key, '四邻': value})
    return result_filename.split('/')[-1]

