from concurrent.futures import ThreadPoolExecutor, as_completed
import cairosvg
import csv

class Template:
    def __init__(self, template_path):
        with open(template_path, 'r') as template_file:
            self.template_string = template_file.read()

    def to_str(self, data = {}):
        outstr = self.template_string
        for key in data:
            outstr = outstr.replace("[{}]".format(key), data[key])
        return outstr

def export_and_send(template, name, email):
    print("[{}] Worker Thread started".format(email))
    cairosvg.svg2pdf(bytestring=template.to_str({"name":name}), write_to="./out/cert_{}.pdf".format(email))
    print("[{}] Finished generating certificate".format(email))

    # todo: Figure out how to send email

    return email

if __name__ == "__main__":
    temp = Template('./template/android.svg')
    list_file = open('list.csv', 'r')
    list_reader = csv.reader(list_file)
    next(list_reader) # header
    
    futures = set()

    with ThreadPoolExecutor(max_workers = 5) as executor:
        for line in list_reader:
            name = line[0].strip()
            email = line[1].strip()
            futures.add(executor.submit(export_and_send, temp, name, email))
        for future in as_completed(futures):
            print("[main] Finished sending email to {}".format(future.result()))
    list_file.close()

    
