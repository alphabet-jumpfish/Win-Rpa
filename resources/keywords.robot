*** Settings ***
Documentation     RPA 自动化自定义关键字库
...               包含针对智能体网站的扩展功能
Library           SeleniumLibrary
Library           Collections
Library           String
Library           DateTime


*** Variables ***
${TIMEOUT}        10s
${SCREENSHOT_DIR}    ${CURDIR}/../logs/screenshots


*** Keywords ***
打开智能体网站
    [Arguments]    ${url}    ${browser}=chrome
    [Documentation]    打开指定的智能体网站
    Open Browser    ${url}    ${browser}
    Maximize Browser Window
    Set Selenium Timeout    ${TIMEOUT}

安全点击元素
    [Arguments]    ${locator}    ${timeout}=${TIMEOUT}
    [Documentation]    等待元素可见后再点击，避免点击失败
    Wait Until Element Is Visible    ${locator}    ${timeout}
    Wait Until Element Is Enabled    ${locator}    ${timeout}
    Sleep    0.5s    # 等待页面稳定
    Click Element    ${locator}

智能输入文本
    [Arguments]    ${locator}    ${text}    ${clear}=${True}
    [Documentation]    先清空输入框再输入文本
    Wait Until Element Is Visible    ${locator}    ${TIMEOUT}
    Run Keyword If    ${clear}    Clear Element Text    ${locator}
    Input Text    ${locator}    ${text}

提取元素文本
    [Arguments]    ${locator}    ${variable_name}=extracted_text
    [Documentation]    提取元素文本内容并保存到变量
    Wait Until Element Is Visible    ${locator}    ${TIMEOUT}
    ${text}=    Get Text    ${locator}
    Log    提取的文本: ${text}
    Set Suite Variable    \${${variable_name}}    ${text}
    [Return]    ${text}

提取多个元素文本
    [Arguments]    ${locator}
    [Documentation]    提取多个元素的文本内容，返回列表
    Wait Until Page Contains Element    ${locator}    ${TIMEOUT}
    @{elements}=    Get WebElements    ${locator}
    @{texts}=    Create List
    FOR    ${element}    IN    @{elements}
        ${text}=    Get Text    ${element}
        Append To List    ${texts}    ${text}
    END
    Log Many    @{texts}
    [Return]    @{texts}

提取元素属性值
    [Arguments]    ${locator}    ${attribute}    ${variable_name}=extracted_attribute
    [Documentation]    提取元素的属性值
    Wait Until Element Is Visible    ${locator}    ${TIMEOUT}
    ${value}=    Get Element Attribute    ${locator}    ${attribute}
    Log    提取的属性 ${attribute}: ${value}
    Set Suite Variable    \${${variable_name}}    ${value}
    [Return]    ${value}

等待并提取文本
    [Arguments]    ${locator}    ${timeout}=30s
    [Documentation]    等待元素出现并提取文本（适用于异步加载的内容）
    Wait Until Element Is Visible    ${locator}    ${timeout}
    Sleep    1s    # 等待内容完全加载
    ${text}=    Get Text    ${locator}
    [Return]    ${text}

滚动到元素位置
    [Arguments]    ${locator}
    [Documentation]    滚动页面使元素可见
    Wait Until Page Contains Element    ${locator}    ${TIMEOUT}
    Scroll Element Into View    ${locator}
    Sleep    0.5s

执行JavaScript并获取结果
    [Arguments]    ${script}
    [Documentation]    执行JavaScript代码并返回结果
    ${result}=    Execute Javascript    ${script}
    Log    JavaScript执行结果: ${result}
    [Return]    ${result}

智能等待页面加载
    [Arguments]    ${timeout}=30s
    [Documentation]    等待页面完全加载
    Wait For Condition    return document.readyState == "complete"    ${timeout}

截图保存
    [Arguments]    ${filename}
    [Documentation]    保存截图到指定位置
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${filepath}=    Set Variable    ${SCREENSHOT_DIR}/${filename}_${timestamp}.png
    Create Directory    ${SCREENSHOT_DIR}
    Capture Page Screenshot    ${filepath}
    Log    截图已保存: ${filepath}
    [Return]    ${filepath}

检查元素是否存在
    [Arguments]    ${locator}    ${timeout}=5s
    [Documentation]    检查元素是否存在，返回布尔值
    ${status}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${locator}    ${timeout}
    [Return]    ${status}

从下拉框选择
    [Arguments]    ${locator}    ${value}
    [Documentation]    从下拉框中选择选项
    Wait Until Element Is Visible    ${locator}    ${TIMEOUT}
    Select From List By Value    ${locator}    ${value}

提取表格数据
    [Arguments]    ${table_locator}
    [Documentation]    提取整个表格的数据
    Wait Until Element Is Visible    ${table_locator}    ${TIMEOUT}
    ${rows}=    Get WebElements    ${table_locator}//tr
    @{table_data}=    Create List
    FOR    ${row}    IN    @{rows}
        ${cells}=    Get WebElements    ${row}//td | ${row}//th
        @{row_data}=    Create List
        FOR    ${cell}    IN    @{cells}
            ${text}=    Get Text    ${cell}
            Append To List    ${row_data}    ${text}
        END
        Append To List    ${table_data}    ${row_data}
    END
    [Return]    ${table_data}

切换到新窗口
    [Documentation]    切换到最新打开的浏览器窗口
    ${handles}=    Get Window Handles
    Switch Window    ${handles}[-1]

关闭当前窗口并返回
    [Documentation]    关闭当前窗口并返回到主窗口
    Close Window
    ${handles}=    Get Window Handles
    Switch Window    ${handles}[0]

执行搜索
    [Arguments]    ${search_box_locator}    ${search_text}    ${search_button_locator}    ${timeout}=${TIMEOUT}
    [Documentation]    在搜索框中输入文本并点击搜索按钮
    智能输入文本    ${search_box_locator}    ${search_text}
    安全点击元素    ${search_button_locator}    ${timeout}
    Log    已执行搜索: ${search_text}
