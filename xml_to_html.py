

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
#from lxml import etree as ET
import datetime
import codecs
import sys



def newlines(s):
	s=s.replace("<br />", "")
	s=s.replace("\r\n","\n")
	s=s.replace("\n","<br />\n")
	
	return s

def fix_xml(xml_file):

	fx = codecs.open('fixed_xml.xml', encoding='utf-8', mode='w')
	not_fixed = codecs.open(xml_file, encoding='utf-8')
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
	return 'fixed_xml.xml'


if __name__ == "__main__":

	file_name = sys.argv[1]
	output_path = sys.argv[2]
	#file_name = path_to_xml_file + 'fixed_xml.xml'
	html_file_name = output_path+'html_test_report_' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H_%M_%S') + '.html'

	tree = ET.parse(fix_xml(file_name))
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
 		<td>Tests passed          </td><td>{1} </tr><tr>
 		<td>Tests failed (failure) </td><td>{2} </tr><tr>
 		<td>Tests failed (error)   </td><td>{3} </tr><tr>
 		<td>Tests skipped          </td><td>{4} </tr>
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
		else:
			color = 'passed'
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


		

