k = "hmiUiVersion="
l = "0.0.0.3"
f = open("/home/kapure/noccarc/Kapure_work/mark_2/Work/development_files/ota_dev/FOTA_improvements/iomt_python_backend/version-list", "r")
data = f.read()
print(data)
print()
for a in data.split():
    if k in a: 
        hmiver = (a.split("="))[1]
        print(hmiver)
        data = data.replace(a, k+l)
f.close()

# g = open("/home/kapure/noccarc/Kapure_work/mark_2/Work/development_files/ota_dev/FOTA_improvements/iomt_python_backend/version-list", "w")
# g.write(data)
# g.close()
