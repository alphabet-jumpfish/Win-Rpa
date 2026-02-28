*** Settings ***
Documentation     1231
Library           SeleniumLibrary
Resource          D:/namespace/python-namespace/Win-Rpa/resources/keywords.robot
Suite Teardown    Close All Browsers

*** Variables ***
${BROWSER}      chrome

*** Test Cases ***
1231
    [Documentation]    自动化执行流程
    打开智能体网站    https://baijiahao.baidu.com/s?id=1858281896268798627&wfr=spider&for=pc    ${BROWSER}