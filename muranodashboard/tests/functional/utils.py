import logging
import os
import yaml
import zipfile

from muranodashboard.tests.functional import consts

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


MANIFEST = {'Format': 'MuranoPL/1.0',
            'Type': 'Application',
            'Description': 'MockApp for webUI tests',
            'Author': 'Mirantis, Inc',
            'UI': 'mock_ui.yaml'}


class ImageException(Exception):
    message = "Image doesn't exist"

    def __init__(self, im_type):
        self._error_string = (self.message + '\nDetails: {0} image is '
                                             'not found,'.format(im_type))

    def __str__(self):
        return self._error_string


def upload_app_package(client, app_name, data):
    try:
        archive = compose_package(app_name, consts.Manifest,
                                  consts.PackageDir)
        package = client.packages.create(data, {app_name: open(archive, 'rb')})
        return package.id
    finally:
        os.remove(archive)
        os.remove(consts.Manifest)


def compose_package(app_name, manifest, package_dir,
                    require=None, archive_dir=None):
    """Composes package `app_name` with `manifest` file as a template for the
    manifest and files from `package_dir`.
    Includes `require` section if any in the manifest file.
    Puts the resulting .zip file into `acrhive_dir` if present or in the
    `package_dir`.
    """
    with open(manifest, 'w') as f:
        fqn = 'io.murano.apps.' + app_name
        mfest_copy = MANIFEST.copy()
        mfest_copy['FullName'] = fqn
        mfest_copy['Name'] = app_name
        mfest_copy['Classes'] = {fqn: 'mock_muranopl.yaml'}
        if require:
            mfest_copy['Require'] = require
        f.write(yaml.dump(mfest_copy, default_flow_style=False))

    name = app_name + '.zip'

    if not archive_dir:
        archive_dir = os.path.dirname(os.path.abspath(__file__))
    archive_path = os.path.join(archive_dir, name)

    with zipfile.ZipFile(archive_path, 'w') as zip_file:
        for root, dirs, files in os.walk(package_dir):
            for f in files:
                zip_file.write(
                    os.path.join(root, f),
                    arcname=os.path.join(os.path.relpath(root, package_dir), f)
                )

    return archive_path
