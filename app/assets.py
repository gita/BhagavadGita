from flask_assets import Bundle

app_css = Bundle('app.scss', filters='scss', output='styles/app.css')

app_js = Bundle('app.js', filters='jsmin', output='scripts/app.js')

vendor_css = Bundle(
    'vendor/bootstrap.min.css',
    'vendor/mdb.min.css',
    'vendor/select2.min.css',
    'vendor/font-awesome.min.css',
    'vendor/bootstrap-social.min.css',
    'vendor/materialize.min.css',
    'vendor/material-icons.css',
    output='styles/vendor.css')

vendor_js = Bundle(
    'vendor/materialize.min.js',
    'vendor/popper.min.js',
    'vendor/bootstrap.min.js',
    'vendor/zxcvbn.js',
    'vendor/clipboard.min.js',
    'vendor/select2.min.js',
    'vendor/axios.min.js',
    'vendor/lazyload.js',
    output='scripts/vendor.js')
