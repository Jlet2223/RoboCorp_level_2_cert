from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )

    download_file()
    orders = get_orders()
    open_robot_order_website()
    close_annoying_modal()
    fill_the_form(orders)
    archive_receipts()


def open_robot_order_website():
    # TODO: Implement your function here
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('Ok')")

def download_file():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def get_orders():
    file = Tables()
    worksheet = file.read_table_from_csv("orders.csv", header=True)
    return worksheet

def fill_the_form(orders):
    page = browser.page()
    for row in orders:
        page.select_option("id=head", row['Head'])
        page.click("id=id-body-"+ row['Body'])
        page.get_by_placeholder("Enter the part number for the legs").fill(row['Legs'])
        page.fill("#address",row['Address'])
        page.click("text=Preview")
        page.click("id=order")
        error_alert = True
        while(error_alert):          
            if(page.content().__contains__("Error")): 
                page.click("id=order")
            else:
                 error_alert = False
        receipt = store_receipt_as_pdf(row['Order number'])
        screenshot = screenshot_robot(row['Order number'])
        embed_screenshot_to_receipt(screenshot,receipt)
        page.click("text=Order another robot")
        close_annoying_modal()
        
        
def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.inner_html("id=receipt")
    path = "output/receipt/" + order_number+ ".pdf"
    pdf = PDF()
    pdf.html_to_pdf(receipt,path)
    return path

def screenshot_robot(order_number):
    page = browser.page()
    path = "output/screenshot/" + order_number+ ".png"
    page.screenshot(path=path)
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    list_of_files = [
        pdf_file,
        screenshot
    ]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document=pdf_file
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipt', 'tasks.zip', recursive=True)
    files = lib.list_archive('tasks.zip')