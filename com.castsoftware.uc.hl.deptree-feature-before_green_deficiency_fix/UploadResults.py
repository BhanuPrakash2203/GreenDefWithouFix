from subprocess import *
import subprocess
from requests import codes
from pandas import DataFrame
from pandas import json_normalize
from pandas import concat
import requests
import time 
import xml.etree.ElementTree as ET
import xml.dom.minidom
from xml.dom import minidom
import os
import re
from lxml import etree
import shutil

class UploadResults():
    def xmlParsing(self,cycloneDXOutput,save_path_file,outputPOM,newOutputFolder):
        #mytree = ET.parse('C:\\DATA\\GITRepo\\com.castsoftware.uc.hl.dt\\response.xml',parser = ET.XMLParser(encoding = 'iso-8859-5'))
        mytree = ET.parse(cycloneDXOutput,parser = ET.XMLParser(encoding = 'iso-8859-5'))
        myroot = mytree.getroot()
        
        root = minidom.Document()
        
        project=root.createElement('project')
        root.appendChild(project)
        project.setAttribute('xmlns','http://maven.apache.org/POM/4.0.0')
        project.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
        project.setAttribute('xsi:schemaLocation','http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd')
        
        modelVersion=root.createElement('modelVersion')
        modelText=root.createTextNode('4.0.0')
        project.appendChild(modelVersion)
        modelVersion.appendChild(modelText)

        xml = root.createElement('dependencies') 
        project.appendChild(xml)

        for dep in myroot.iter('{http://cyclonedx.org/schema/bom/1.4}dependency'):
            components=dep.get('ref')
            #print(dep.get('ref'))
            
            depsChild = root.createElement('dependency')
            xml.appendChild(depsChild)
            
            groupID = root.createElement('groupId')
            textgroupID=root.createTextNode(components.partition(':')[0])
            #textgroupID=root.createTextNode(components)
            depsChild.appendChild(groupID)
            groupID.appendChild(textgroupID)
            

            artifactId=root.createElement('artifactId')
            textartifactId=root.createTextNode(components.partition(':')[2].partition('@')[0])
            #textartifactId=root.createTextNode(components)
            depsChild.appendChild(artifactId)
            artifactId.appendChild(textartifactId)

            version=root.createElement('version')
            textversion=root.createTextNode(components.partition(':')[2].partition('@')[2])
            #textversion=root.createTextNode(components)
            depsChild.appendChild(version)
            version.appendChild(textversion)


        xml_str = root.toprettyxml(indent ="\t") 
        
        if not os.path.exists(newOutputFolder):
            # if the demo_folder directory is not present 
            # then create it.
            os.makedirs(newOutputFolder)
        outPath=os.listdir(newOutputFolder)    
        if len(outPath)==0:
            shutil.copy(outputPOM,newOutputFolder)
        
        with open(save_path_file, "w+") as f:
            f.write(xml_str) 
        
        self.removeDuplicateTags(save_path_file,newOutputFolder)
            
    def removeDuplicateTags(self,save_path_file,outputPOM):
        
        outputPOM=outputPOM+'\pom.xml'
        file = open(outputPOM, "r")
        #read content of file to string
        data = file.read()
        #get number of occurrences of the substring in the string
        global occurrences_previous
        occurrences_previous = data.count("<dependency>")   

        unique_tag_list=[]
        unwanted_tag_list=[]
        tag_list_1=[]
        tag_list_2=[]
        tag_list_3=['\n\t</dependencies>\n','</project>']

        #extrating required data from xml using regex
        with open(save_path_file, 'r') as f:
            content = f.read()

            #
            tag_pattern_1='(<\?xml (?:.|\n)+?.*<dependencies>)'
            tag_list_1=re.findall(tag_pattern_1,content)

            #extracting all the dependencies 
            tag_pattern_2='(<dependency>(?:.|\n)+?.*</dependency>)'
            tag_list_2=re.findall(tag_pattern_2,content)

            if len(tag_list_2)>0:
                for tag in tag_list_2:
                    if tag not in unique_tag_list:
                        #storing unqing dependencies to unique_tag_list
                        unique_tag_list.append(tag)
                    else:
                        unwanted_tag_list.append(tag)

        for i in range(len(unique_tag_list)):
            unique_tag_list[i]='\n\t\t'+unique_tag_list[i]

        #Combining all the data together
        tag_list_1.extend(unique_tag_list)
        tag_list_1.extend(tag_list_3)

        
        #writing combined data together to a output xml file
        with open(outputPOM, "w+") as f2:
            for i in tag_list_1:
                f2.write(i)
        file = open(outputPOM, "r")
        #read content of file to string
        data = file.read()
        #get number of occurrences of the substring in the string
        global occurrences_latest
        occurrences_latest = data.count("<dependency>")   


start_time = time.time()

print('Copyright (c) 2023 CAST Software Inc.\n')
print('If you need assistance, please contact Bhanu Prakash (BBA) from the CAST IN PS team\n')

 
#HL Command line parameters
#extract parameters from properties.txt file
dirname = os.path.dirname(__file__)
properties_file=dirname+'\\Configuration\\Properties.txt'
with open(properties_file,'r') as f:
    path_list = f.read().split('\n')
    
    cycloneDXOutput=path_list[9].strip()
    save_path_file=path_list[10].strip()
    outputPOM=path_list[11].strip()
    newOutputFolder=path_list[12].strip()


if cycloneDXOutput=='cycloneDXOutput=':
    print('Output CycloneDX path is not defined')
    exit()

if save_path_file=='save_path_file=':
    print('Parsed POM.xml path is not defined')
    exit()           

if outputPOM=='outputPOM=':
    print('Output POM location is not defined')
    exit()    

if newOutputFolder=='newOutputFolder=':
    print('New output POM directory path is not defined')
    exit()


cycloneDXOutput=cycloneDXOutput.split('=')
cycloneDXOutput=cycloneDXOutput[1]

save_path_file=save_path_file.split('=')
save_path_file=save_path_file[1]

outputPOM=outputPOM.split('=')
outputPOM=outputPOM[1]

newOutputFolder=newOutputFolder.split('=')
newOutputFolder=newOutputFolder[1]

#Arguments to pass in HighlightAutomation 
#args = [f'{hlJarPath}', '--sourceDir', f'{sourceDir}', '--workingDir' , f'{workingDir}', '--analyzerDir', f'{analyzerDir}', '--companyId', f'{companyId}', '--applicationId', f'{applicationId}', '--snapshotLabel', f'{snapshotLabel}', '--basicAuth', f'{basicAuth}', '--serverUrl', f'{serverUrl}'] # Any number of args to be passed to the jar file

#Number of <dependency> tags pereviously and in latest POM XML

obj=UploadResults()

for iter in range(80000):
        #3. Parse response XML (BOM) and generate a new pom.xml for HL Scan and relaunch the scan
        try:
            #start_time_xml_parsing = time.time()
            obj.xmlParsing(cycloneDXOutput,save_path_file,outputPOM,newOutputFolder)
            #end_time_xml_parsing = time.time()
            #execution_time_xml_parsing = end_time_xml_parsing - start_time_xml_parsing
            #toatal_xml_parsing_time = toatal_xml_parsing_time + execution_time_xml_parsing
            #print(f"For Loop Number {iter} Execution time for XML Parsing: {execution_time_xml_parsing} seconds") 
        except:
            print('Error occurred during Parsing BOM')
            exit()
    
# Record the end time
end_time = time.time()

# Calculate the execution time in seconds
execution_time = end_time - start_time


#print(f"Total Execution time to run XML Parsing : {toatal_xml_parsing_time} seconds")
print(f"Total Execution time to run program for {iter} loops : {execution_time} seconds") 