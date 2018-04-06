
#init python:
#    import time
#    import pygame
#    import shader
#    from OpenGL import GL as gl
    
#    PS_MASTER_LR2 = """
#        VARYING vec2 varUv;

#        UNIFORM sampler2D tex0;
#        UNIFORM sampler2D tex1;
#        UNIFORM float shownTime;
#        UNIFORM float animationTime;

#        void main()
#        {
#            vec4 color1 = texture2D(tex0, varUv);
#            vec4 weights = texture2D(tex1, varUv);
#            float influence = weights.r;

#            if (influence > 0.0) {
#                float speed = sin(animationTime * 5.0);
#                float xShift = sin(speed + varUv.x * varUv.y * 10) * influence * 0.01;
#                float yShift = cos(speed + varUv.x * varUv.y * 5) * influence * 0.01;

#                gl_FragColor = texture2D(tex0, varUv + vec2(xShift, yShift));
#            }
#            else {
#                gl_FragColor = color1;
#            }
#        }
#    """
    
#    PS_COLOUR_SUB_LR2 = """
#        VARYING vec2 varUv; //Texture coordinates

#        UNIFORM sampler2D tex0; //Texture bound to slot 0
#        UNIFORM float shownTime; //RenPy provided displayable time

#        UNIFORM vec4 colour_levels;
        
#        void main()
#        {
#            vec4 color = texture2D(tex0, varUv);
#            float red = color.r * colour_levels.r;
#            float green = color.g * colour_levels.g;
#            float blue = color.b * colour_levels.b;
#            float alpha = color.a * colour_levels.a;
#            gl_FragColor = vec4(red, green, blue, alpha);
#        }
#    """

#    if persistent.shader_effects_enabled is None:
#        persistent.shader_effects_enabled = True

#    def _interactCallback():
#        shader._controllerContextStore.checkDisplayableVisibility(ShaderDisplayable)

#    def _initContextCallbacks():
#        shader._setupRenpyHooks()
#        if not _interactCallback in renpy.config.interact_callbacks:
#            renpy.config.interact_callbacks.append(_interactCallback)

#    class ShaderDisplayable(renpy.Displayable):
#        def __init__(self, mode, image, vertexShader, pixelShader, textures=None, uniforms=None, create=None, update=None, args=None, **properties):
#            super(ShaderDisplayable, self).__init__(**properties)

#            self.mode = mode
#            self.image = renpy.displayable(image)
#            self.vertexShader = vertexShader
#            self.pixelShader = pixelShader
#            self.textures = textures
#            self.uniforms = uniforms
#            self.createCallback = create
#            self.updateCallback = update
#            self.tag = mode + "/" + image + "/" + vertexShader + "/" + pixelShader + "/" + str(textures) + "/" + str(uniforms) + "/" + str(args)
#            self.args = args or {}

#            self.mousePos = (0, 0)
#            self.mouseVelocity = (0, 0)
#            self.events = []

#            if not renpy.predicting():
#                _initContextCallbacks()

#        def getContext(self):
#            return shader._controllerContextStore.get(self.tag)

#        def setController(self, controller):
#            context = self.getContext()
#            context.freeController()
#            context.persist = self.args.get("persist")
#            context.controller = controller
#            context.createCalled = False
#            if controller:
#                context.updateModeChangeCount()

#        def createController(self):
#            renderer = None
#            if self.mode == shader.MODE_2D:
#                renderer = shader.Renderer2D()
#                renderer.init(self.image, self.vertexShader, self.pixelShader)
#            elif self.mode == shader.MODE_3D:
#                w, h = renpy.display.im.load_surface(self.image).get_size()
#                renderer = shader.Renderer3D()
#                renderer.init(self.vertexShader, self.pixelShader, w, h)
#            elif self.mode == shader.MODE_SKINNED:
#                renderer = shader.SkinnedRenderer()
#                renderer.init(self.image, self.vertexShader, self.pixelShader, self.args)
#            else:
#                raise RuntimeError("Unknown mode: %s" % self.mode)

#            renderController = shader.RenderController()
#            renderController.init(renderer)

#            return renderController

#        def freeController(self):
#            self.setController(None)

#        def resetController(self):
#            self.freeController()

#            try:
#                controller = self.createController()

#                if self.textures:
#                    for sampler, name in self.textures.items():
#                        controller.renderer.setTexture(sampler, renpy.displayable(name))

#                self.setController(controller)
#            except gl.GLError as e:
#                #Try again later
#                shader.log("Render controller reset error: %s" % e)

#        def checkModeChangeCount(self):
#            if self.getContext().modeChangeCount != shader.getModeChangeCount():
#                self.resetController()

#        def checkOpenGLState(self):
#            oldError = gl.glGetError() #Get and clear error flag
#            if oldError != gl.GL_NO_ERROR and config.developer:
#                #This is not vital, but if RenPy (or us) has previously caused an error state
#                #this will let us know about it so we can investigate more. Also otherwise
#                #it will be automatically converted into an exception which we don't want.
#                shader.log("Unknown developer mode OpenGL error: %s" % oldError)

#        def render(self, width, height, st, at):
#            result = None

#            if persistent.shader_effects_enabled and not renpy.predicting() and shader.isSupported():
#                self.checkOpenGLState()

#                context = self.getContext()
#                if not context.controller:
#                    self.resetController()

#                self.checkModeChangeCount()

#                context = self.getContext()
#                if context.controller:
#                    controller = context.controller

#                    renderWidth, renderHeight = controller.getSize()
#                    result = renpy.Render(renderWidth, renderHeight)
#                    canvas = result.canvas() #TODO Slow, allocates one surface every time...
#                    surface = canvas.get_surface()

#                    uniforms = {
#                        "shownTime": st,
#                        "animationTime": at,
#                        "mousePos": self.screenToTexture(self.mousePos, width, height),
#                        "mouseVelocity": self.mouseVelocity,
#                    }
#                    if self.uniforms:
#                        uniforms.update(self.uniforms)

#                    overlayRender = renpy.Render(renderWidth, renderHeight)
#                    renderContext = shader.RenderContext(controller.renderer,
#                        renderWidth, renderHeight, time.time(), st, at, uniforms,
#                        self.mousePos, self.events, context.contextStore, overlayRender)

#                    self.events = []

#                    if self.createCallback and not context.createCalled:
#                        context.createCalled = True
#                        self.createCallback(renderContext)

#                    if self.updateCallback:
#                        self.updateCallback(renderContext)

#                    if renderContext.overlayCanvas:
#                        #Overlay canvas was created and used
#                        result.blit(overlayRender, (0, 0))

#                    continueRendering = renderContext.continueRendering

#                    try:
#                        controller.renderImage(renderContext)
#                        controller.copyRenderBufferToSurface(surface)
#                    except gl.GLError as e:
#                        shader.log("Render controller render error: %s" % e)
#                        #Free controller and try again later
#                        self.freeController()
#                        continueRendering = False
#                        result = None

#                    if continueRendering:
#                        renpy.redraw(self, 1.0 / shader.config.fps)

#            if not result:
#                #Original image
#                result = renpy.render(self.image, width, height, st, at)

#            return result

#        def screenToTexture(self, pos, width, height):
#            if pos:
#                #Only makes sense with untransformed fullscreen images...
#                return (pos[0] / float(width), pos[1] / float(height))
#            return (-1.0, -1.0)

#        def event(self, ev, x, y, st):
#            self.events.append((ev, (x, y)))
#            while len(self.events) > 100:
#                #Too many, remove oldest
#                self.events.pop(0)

#            if ev.type == pygame.MOUSEMOTION or ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEBUTTONUP:
#                self.mousePos = (x, y)

#        def visit(self):
#            return [self.image]
