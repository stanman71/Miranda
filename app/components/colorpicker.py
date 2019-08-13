"""

Flask-Colorpicker
-------------
A Flask extension to add Spectrum javascript color picker into the template,
it makes adding and configuring multiple color pickers at a time much easier
and less time consuming

author = Mohamed Feddad

https://github.com/mrf345/flask_colorpicker/ 

"""

from flask import Markup


class colorpicker(object):

    def __init__(self, host, app=None):
       
        self.host = host
        
        self.app  = app
        if self.app is not None:
            self.init_app(app)
        else:
            raise(AttributeError("must pass app to colorpicker(app=)"))
                
        self.injectThem()  # injecting module into the template


    def init_app(self, app):
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        pass

    def injectThem(self):
        """ to inject the module into the template as colorpicker """
        @self.app.context_processor
        def inject_vars():
            return dict(colorpicker=self)

    def loader(self):
        html = ""
        for i, n in enumerate(['js', 'css']):

            # IMPORTANT: Update the links 
            # Windows: 127.0.0.1
            # RasPi: IP of the RasPi
            
            links = ['http://' + self.host + '/get_media/spectrum.css',
                     'http://' + self.host + '/get_media/spectrum.js'] 
            tags = [
            '<script src="%s"></script>\n',
            '<link href="%s" rel="stylesheet">\n'
            ] 
            html += tags[i] % [
                l for l in links if l.split(
                    '.')[len(l.split('.')) - 1] == n][0]

        return Markup(html)


    def picker(self, ids=[".colorpicker"],
               default_color='rgb(0,0,255)',
               color_format='rgb',
               showAlpha='true',
               showInput='false',
               showButtons='false',
               allowEmpty='true'):
       
        for h, a in {'showAlpha': showAlpha,
                     'showInput': showInput,
                     'showButtons': showButtons,
                     'allowEmpty': allowEmpty}.items():
            if not isinstance(a, str):
                raise(TypeError("colorpicker.picker(%s) takes string" % h))
            if h != 'id' and a != 'true' and a != 'false':
                raise(TypeError(
                    "colorpicker.picker(%s) only true or false string" % h))
            if not isinstance(ids, list):
                raise(TypeError("colorpicker.picker(ids) requires a list of strings"))
        html = ""
        
        for id in ids:
            html += " ".join([
                '<script> $(document).ready(function () {'
                '$("%s").spectrum({' % id,
                'showAlpha: %s,' % showAlpha,
                'showInput: %s,' % showInput,
                'showButtons: %s,' % showButtons,
                'allowEmpty: %s,' % allowEmpty,
                'color: $("%s").val() || "%s",' % (id, default_color),
                'preferredFormat: "%s",' % color_format,
                'move: function(color) {',
                '$(this).val(color.toRgbString())',
                '},', '})',
                '}) </script>'])
                
        return Markup(html) # html ready colorpicker