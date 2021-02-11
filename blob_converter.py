import base64

file_path = 'C:/Users/Geops/Desktop/Projekt BD/REST_API_Medic_System' #YOUR PATH
with open(file_path+'/input_pdf.pdf', 'rb') as f:
    blob = base64.b64encode(f.read())

text_file = open('test_blob.txt', "wb")
text_file.write(blob)
text_file.close()

with open('test_blob.txt', 'r') as f:
    blob=f.read()

blob = base64.b64decode(blob)

text_file = open('result_pdf.pdf','wb')
text_file.write(blob)
text_file.close()
