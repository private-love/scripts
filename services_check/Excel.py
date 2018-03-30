#!/bin/env python
#coding:utf-8

import os, time, sys
import xdrlib
import xlrd
import xlwt
import xlsxwriter

reload(sys)
sys.setdefaultencoding('utf-8')

class Excel:
	"""
	excel报表生成模块
	"""
	workbook = None
	excel_filename = None
	sheet_name = None
	encoding = None
	cell_format = None
	bold = None

	def __init__(self, filename, sheet_name='ciSheet', encoding='utf-8',is_xlsx=True) :
		self.excel_filename = filename
		self.sheet_name = sheet_name
		self.encoding = encoding
		if is_xlsx :
			self.workbook = xlsxwriter.Workbook(self.excel_filename)
			self.cell_format = self.workbook.add_format({'align': 'center','valign': 'vcenter','border': 1})
			self.bold = self.workbook.add_format({'bold': 1})

	def open_excel(self) :
      		"""读取xls文件内容"""
        	try:
       	        	data = xlrd.open_workbook(self.excel_filename)
        	        return data
        	except Exception,e:
        	        print str(e)
	
	def excel_table_byindex(self, colnameindex=0,by_index=0):
        	"""
        	   根据索引获取Excel表格中的数据
        	   参数:
        	          file：Excel文件路径
        	          colnameindex：表头列名所在行的索引
        	          by_index：表的索引
        	"""
        	data = self.open_excel()
        	table = data.sheets()[by_index]
        	nrows = table.nrows #行数
        	ncols = table.ncols #列数
        	colnames =  table.row_values(colnameindex) #某一行数据
        	list =[]

        	for rownum in range(1,nrows):
        	        row = table.row_values(rownum)
        	        if row:
        	                app = {}
        	                for i in range(len(colnames)):
        	                        app[colnames[i]] = row[i]
        	                list.append(app)
        	return list

	def excel_table_byname(self, colnameindex=0,by_name=u'Sheet1'):
        	"""
        	   根据索引获取Excel表格中的数据
        	   参数:
        	          file：Excel文件路径
        	          colnameindex：表头列名所在行的索引
        	          by_name：Sheet1名称
        	"""
        	data = self.open_excel()
        	table = data.sheet_by_name(by_name)
        	nrows = table.nrows
        	colnames =  table.row_values(colnameindex)
        	list =[]
        	for rownum in range(1,nrows):
        	        row = table.row_values(rownum)
        	        if row:
        	                app = {}
        	                for i in range(len(colnames)):
        	                        app[colnames[i]] = row[i]
        	                list.append(app)
        	return list

	def write_xls(self, headings, data, heading_xf, data_xfs):
        	"""
        	汇总各项统计xls写入样式
        	参数：
        	        file_name : xls文件名
        	        sheet_name : sheet名称
        	        headings : 标题名称列表
        	        data ：表格数据列表
        	        heading_xf : 标题样式
        	        data_xfs : 数据样式
        	"""
        	book = xlwt.Workbook(self.encoding)
        	sheet = book.add_sheet(self.sheet_name)
        	rowx = 0
        	for colx, value in enumerate(headings):
        	        sheet.write(rowx, colx, value, heading_xf)
        	sheet.set_panes_frozen(True) # frozen headings instead of split panes
        	sheet.set_horz_split_pos(rowx+1) # in general, freeze after last heading row
        	sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
        	for row in data:
        	        rowx += 1
        	        for colx, value in enumerate(row):
        	                #print str(value)+"长度:"+str(len(str(value)))
        	                if len(str(value)) > 10 :
        	                        sheet.col(colx).width = 256 * (len(str(value))+1)
        	                sheet.write(rowx, colx, value, data_xfs[colx])
        	book.save(self.excel_filename)

	def serverlist_info_xls_write(self, data) :
		"""
		输出服务器信息报表
		"""
        	ezxf = xlwt.easyxf
        	hdngs = ['序号', 'IP', '服务器型号', '服务器序列号', 'CPU信息','CPU个数','CPU内核数','CPU线程数','CPU超频','内存大小','Raid信息', 'OS>版本','OS内核','Hostname',]
        	kinds =  'int service_tag text service_tag text service_tag text text text service_tag text service_tag text text'.split()
        	heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
        	kind_to_xf_map = {
        	        'date': ezxf(num_format_str='yyyy-mm-dd'),
        	        'int': ezxf(num_format_str='#,##0'),
        	        'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
        	            num_format_str='$#,##0.00'),
        	        'price': ezxf(num_format_str='#0.000000'),
        	        'service_tag':ezxf('font: italic on; pattern: pattern solid, fore-colour grey25'),
        	        'text': ezxf(),
        	        }
        	data_xfs = [kind_to_xf_map[k] for k in kinds]
        	self.write_xls(hdngs, data, heading_xf, data_xfs)

	def serverlist_info_xlsx_autofilter_write(self, data) :
		"""
		输出服务器信息报表，并自动归类
		"""
        	#workbook = xlsxwriter.Workbook(file_name)
        	worksheet = self.workbook.add_worksheet()
        	#bold = workbook.add_format({'bold': 1})
        	hdngs = ['服务器型号', 'CPU信息','CPU个数','CPU内核数','CPU线程数','CPU超频','内存大小', 'OS版本','OS内核']
        	worksheet.set_column('A:I', 24)
        	worksheet.set_row(0, 20, self.bold)
        	worksheet.write_row('A1', hdngs)
        	worksheet.autofilter('A1:I55')
        	row = 1
        	for row_data in (data):
        	        row_data_new = []
        	        row_data_new.append(row_data[2])
        	        row_data_new.append(row_data[4])
        	        row_data_new.append(row_data[5])
        	        row_data_new.append(row_data[6])
        	        row_data_new.append(row_data[7])
        	        row_data_new.append(row_data[8])
        	        row_data_new.append(row_data[9])
        	        row_data_new.append(row_data[11])
        	        row_data_new.append(row_data[12])
        	        worksheet.write_row(row, 0, row_data_new)
        	        row += 1
		self.workbook.close()

	def backup_xlsx_write(self, hdngs, data):
        	"""
		backup_table_wirte(file_name, sheet_name, data)
        	将备份检查数据生成报表
        	"""
        	worksheet = self.workbook.add_worksheet()
        	#hdngs = ['服务器IP', '备份昵称','备份日期','备份大小','备份文件名','备份目录']
        	#worksheet.set_column('A:F', 24)
		worksheet.set_column(0, len(hdngs)-1, 24)
        	worksheet.set_row(0, 20, self.bold)
        	worksheet.write_row('A1', hdngs)
        	#worksheet.autofilter('A1:F55')
        	row_num = 1
        	col_num = 1
        	merge_row = 1
        	key_list = []
        	dict = {}
        	for row in (data):
        	        row_data = []
        	        row_data = row[0].split(',')
        	        key = row_data[0]
        	        value = row_data[1:]
        	        if key not in key_list :
        	                key_list.append(key)
        	                dict[key] = []
        	                dict[key].append(value)
        	        else :
        	                dict[key].append(value)

		for (k,val) in dict.items():
        	        merge_num = len(val)
        	        #print k,merge_row,merge_num,merge_row+merge_num
        	        if merge_num > 1 :
        	                worksheet.merge_range(merge_row,0,merge_row+merge_num-1,0,k,self.cell_format)
        	        else :
        	                worksheet.write(merge_row, 0, k, self.cell_format)

        	        for item in val :
        	                worksheet.write_row(row_num, 1, item)
        	                row_num += 1
        	        merge_row = merge_row+merge_num
        	#print "总共记录:"+str(row_num)
        	self.workbook.close()
