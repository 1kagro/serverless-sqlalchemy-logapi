from Utils.Aws import Aws

class Template:
    
    def __init__(self, template_name):
        __s3 = Aws.get_secret('s3-fcc')
        self.template_name = template_name
        self.template_path = f"Templates/{self.template_name}"
        self.template_path_aws = f"{__s3['template_email_folder']}/{self.template_name}"
        self.bucket_name = __s3['bucket_name']

    def get_local_template(self):
        
        template_content = ''
        with open(self.template_path, 'r') as f:
            template_content = f.read()

        return template_content

    def get_with_replace_var(self, old: str, new: str) -> str:
        """
        Obtener el template en string y reemplazar la variable
        :param: old
            variable a reemplazar
        :param: new
            variable a reemplazar
        """
        # template_content = self.get_template()
        s3_object = Aws.get_object(self.bucket_name, self.template_path_aws)
        if s3_object:
            template_content = s3_object.decode('utf-8')
            s3_object = template_content.replace(old, new)
        return s3_object
