import locale
import tempfile
import ghostscript
from google.cloud import storage

storage_client = storage.Client()

def convert_pdf(event, context):
    storage_client = storage.Client()
    bucket_name = event['bucket']
    pdf = event['name']
    if pdf.startswith('v-'):
        return
    print('starting converting..')
    blob = storage_client.bucket(bucket_name).get_blob(pdf)

    _, tmp_pdf = tempfile.mkstemp()
    _, tmp_png = tempfile.mkstemp()

    tmp_png = tmp_png+".png"

    blob.download_to_filename(tmp_pdf)
    print('download success')

    # create a temp folder based on temp_local_filename
    # use ghostscript to export the pdf into pages as pngs in the temp dir
    args = [
        "pdf2png", # actual value doesn't matter
        "-dSAFER",
        "-sDEVICE=pngalpha",
        "-o", tmp_png,
        "-r300", tmp_pdf
        ]
    print('export success')
    # the above arguments have to be bytes, encode them
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]
    #run the request through ghostscript
    ghostscript.Ghostscript(*args)

    print("Image created")
    new_file_name = "v-"+pdf.split('.')[0]+".png"
    blob.bucket.blob(new_file_name).upload_from_filename(tmp_png)
