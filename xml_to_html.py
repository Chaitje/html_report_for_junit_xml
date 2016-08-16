

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
#from lxml import etree as ET
import datetime
import codecs
import sys
import os
import time



def newlines(s):
	s=s.replace("<br />", "")
	s=s.replace("\r\n","\n")
	s=s.replace("\n","<br />\n")
	
	return s

def fix_xml(xml_files, working_path):
	fixed_xmls = []
	for xml_file in xml_files:
		fixed_xml_name = working_path +'fixed_' + xml_file
		fx = codecs.open(fixed_xml_name, encoding='utf-8', mode='w')
		not_fixed = codecs.open(working_path + xml_file, encoding='utf-8')
		content = not_fixed.readlines()
		for line in content:
			if '\a' in line:
				line_repl = line.replace('\a', '\\a')
				print >> fx, line_repl
			elif '\b' in line:
				line_repl = line.replace('\b', '\\b')
				print >> fx, line_repl
			else:
				print >> fx, line
		fx.close()
		not_fixed.close()
		fixed_xmls.append(fixed_xml_name)

	return (fixed_xmls)


def combine_xmls(xml_files, working_path):

	errors = 0
	failures =  0
	names = []
	skipped = 0
	tests = 0
	time = 0
	rest_of_xmls = []
	declaration_string = "<?xml version='1.0' encoding='UTF-8'?>"
	end_string = '</testsuite>'
	

	for xml in xml_files:
		print("ik ga nu kijken naar {}".format(xml))
		tree = ET.parse(xml)
		root = tree.getroot()

		failure = root.attrib['failures']
		error = root.attrib['errors']
		name = root.attrib['name']
		skip = root.attrib['skipped']
		test = root.attrib['tests']
		t = root.attrib['time']

		errors += int(error)
		failures += int(failure)
		names.append(name)
		skipped += int(skip)
		tests += int(test)
		time += float(t)

		summary_string = '<testsuite errors="{0}" failures="{1}" name="{2}" skipped="{3}" tests="{4}" time="{5}">'.format(str(error), str(failure), name, str(skip), str(test),str(t))

		with codecs.open(xml, encoding='UTF-8') as f:
			all_lines = f.read()
			reduced_xml = all_lines.replace(declaration_string,'')
			reduced_xml = reduced_xml.replace(summary_string,'')
			reduced_xml = reduced_xml.replace('</testsuite>', '')
			rest_of_xmls.append(reduced_xml)

	summary_string_total =  '''
	<testsuite errors="{0}" failures="{1}" name="{2}" skipped="{3}" tests="{4}" time="{5}">
	'''.format(str(errors), str(failures), 'the amazing RT', str(skipped), str(tests),str(time))

	xml_combine = codecs.open(working_path + 'combined_xml.xml', encoding='utf-8', mode='w')
	print >> xml_combine, declaration_string
	print >> xml_combine, summary_string_total
	for rest_string in rest_of_xmls:
		print >> xml_combine, unicode(rest_string)
	print >> xml_combine, end_string
	xml_combine.close()
	return 'combined_xml.xml'




def find_xmls(working_path):

	#wait for and find the junit xml files in directory
	xml_files =[]
	files_found = False
	extra_turn = False
	while files_found == False:
		all_files_in_dir = os.listdir(working_path)
		for file in all_files_in_dir:
			if file.endswith('xml'):
				if file not in xml_files:
					xml_files.append(file)
					print('voor nu: aantal xmls gevonden '+ str(len(xml_files)))
		if len(xml_files)==0:
			time.sleep(2)
		else:
			if extra_turn == False:
				time.sleep(6)
				extra_turn = True
			elif extra_turn == True:
				files_found = True
	return xml_files



if __name__ == "__main__":

	working_path = sys.argv[1]
	xml_files = find_xmls(working_path)
	fixed_xmls = fix_xml(xml_files, working_path)
	file_name = combine_xmls(fixed_xmls, working_path)
		
	#Parse the xml and write the html file

	html_file_name = working_path+'Test_report_'  + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H_%M_%S') + '.html'

	tree = ET.parse((working_path + file_name, working_path))
	root = tree.getroot()
	html_string = u""""""
	html_string_top = """
		<!doctype html>
<html>
	<head>
		<meta charset="utf-8">
		<title>Test</title>
		<script language="javascript"> 
function toggle(elementId) {
	var ele = document.getElementById(elementId);
	if(ele.style.display == "block") {
    		ele.style.display = "none";
  	}
	else {
		ele.style.display = "block";
	}
} 
</script><style>
.summary{
  font-size: 150%;
  font_weight: bold;
  border: 1px solid black;
}
.summary td {
padding: 5px;
}
.details{
	border-collapse: collapse;
}
.stacktrace{
  font-size: 90%
}
.scenario{
  font-size: 80%
}
.scenario_name{
  font-size: 110%
}
.stdout{
  font-size: 80%
}
.error{
  font-size: 90%
}
.passed{
  color: #1ACC02
}
.failed{
  color: #BF3115 
}
.skipped{
  color: #C4A499
}


</style>
	</head>
	<body>
	"""

	html_string_bottom = """
		</table><br /><br />
		</body>
</html>"""



	
	f = codecs.open(html_file_name, encoding='utf-8', mode='w')
	print >> f, html_string_top
	test_summary_failures = root.attrib['failures']
	test_summary_errors = root.attrib['errors']
	test_summary_tests = root.attrib['tests']
	test_summary_skipped = root.attrib['skipped']
	test_summary_passed = unicode(int(test_summary_tests) - int(test_summary_failures) - int(test_summary_errors) - int(test_summary_skipped))
 	
 	test_summary = """
 		<table class = \"summary\" ><tr>
 		<td>Total number of tests        </td><td> {0} </tr><tr>
 		<td class = "passed">Tests passed          </td><td class = "passed">{1} </tr><tr>
 		<td class = "failed">Tests failed (failure) </td><td class = "failed">{2} </tr><tr>
 		<td class = "failed">Tests failed (error)   </td><td class = "failed">{3} </tr><tr>
 		<td class = "skipped">Tests skipped          </td><td class = "skipped">{4} </tr>
 		</table><table class ="details"><br/>
 		""".format(test_summary_tests, test_summary_passed, test_summary_failures,test_summary_errors, test_summary_skipped)
 	print >> f,  test_summary
	for child in root:

		status = child.get('status')
		scenario_naam = child.get('name')
		feature = child.get('classname')
		try:
			sysout =  child.find('system-out').text
		except:
			pass
		scenario, stdout_capture = sysout.split('@scenario.end')
		scenario = '<pre class = "scenario">' + scenario + '</pre>'
		stdout_capture = '<div class = "stdout">' + stdout_capture + '</div>'
		


		error_msg = ''
		failure_msg = ''
		if status =='failed':
			color = 'failed'
		elif status == 'passed':
			color = 'passed'
		elif status == 'skipped':
			color = 'skipped'
		link_regel = '<tr><td><a class= "scenario_name {0}" id="displayText" href="javascript:toggle(\'{1}\');">{1}</a></td><td><a class= "scenario_name {0}" id="displayText" href="javascript:toggle(\'{1}\');">{2}</a></tr>'.format(color, scenario_naam, status)
		print >> f, link_regel
		test_report_msg =""""""
		if status =='failed':
			try:
				error_msg = '<pre class = "error">' + child.find('error').text + '</pre>'
				test_report_msg = test_report_msg + error_msg
				#print >> f, newlines(error_msg) + '<br />'
			except AttributeError:
				failure_msg = unicode(child.find('failure').attrib['type']) + ': ' + unicode(child.find('failure').attrib['message'])
				failure_msg = '<br /><div class = "error">' + failure_msg + '</div>'
				test_report_msg = unicode(test_report_msg) + unicode(failure_msg)
				#print >> f, newlines(unicode(failure_msg)) + '<br />'
		test_report_msg = test_report_msg + newlines(scenario) + newlines(stdout_capture)

		#test_report_msg = '<div id="toggleText2" style="display: none" href="javascript:toggle();">{}</div>'.format(unicode(test_report_msg))
		print >> f,  '<tr><td><div id="{}" style="display: none" href="javascript:toggle();">'.format(scenario_naam)
		print >> f,  test_report_msg
		print >> f,  '</div></td></tr>'
	print >> f, html_string_bottom
	f.close()

	all_file_in_path = os.listdir(working_path)
	xmls_in_path = []
	for file in all_file_in_path:
		if file.endswith('.xml'):
			os.remove(working_path +  file)
	

		

