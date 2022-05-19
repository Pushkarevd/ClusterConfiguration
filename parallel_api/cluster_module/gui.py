import sys

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

path_to_font = r"C:\Users\Пушкарев Даниил\PycharmProjects\ClusterConfiguration\parallel_api\cluster_module\constan.ttf"


def render_frame(impl, window, font, machines):
    glfw.poll_events()
    impl.process_inputs()
    imgui.new_frame()

    gl.glClearColor(0.1, 0.1, 0.1, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    if font is not None:
        imgui.push_font(font)
    new_frame(machines)
    if font is not None:
        imgui.pop_font()

    imgui.render()
    impl.render(imgui.get_draw_data())
    glfw.swap_buffers(window)


def new_frame(machines):
    io = imgui.get_io()

    if io.key_ctrl and io.keys_down[glfw.KEY_Q]:
        sys.exit(0)

    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Cluster", True):
            clicked_quit, selected_quit = imgui.menu_item("Exit", "Ctrl+Q", False, True)

            if clicked_quit:
                sys.exit(0)

            imgui.end_menu()
        imgui.end_main_menu_bar()

    imgui.begin("Example: Columns - File list")
    imgui.columns(5, 'clusterTable')
    imgui.separator()
    imgui.text("Machine Name")
    imgui.next_column()
    imgui.text("IP")
    imgui.next_column()
    imgui.text("Number of cores")
    imgui.next_column()
    imgui.text("Ram usage")
    imgui.next_column()
    imgui.text("Cpu usage")
    imgui.next_column()
    imgui.separator()

    for info in machines.values():
        imgui.text(info.get('name'))
        imgui.next_column()
        imgui.text(info.get('ip'))
        imgui.next_column()
        imgui.text(str(info.get('cores')))
        imgui.next_column()
        imgui.text(str(info.get('ram')))
        imgui.next_column()
        imgui.text(str(info.get('cpu')))
        imgui.next_column()

    imgui.columns(1)

    imgui.end()


def impl_glfw_init():
    width, height = 1800, 450
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


def start_gui(machines):
    imgui.create_context()
    window = impl_glfw_init()

    impl = GlfwRenderer(window)

    io = imgui.get_io()
    jb = io.fonts.add_font_from_file_ttf(path_to_font, 30) if path_to_font is not None else None
    impl.refresh_font_texture()

    while not glfw.window_should_close(window):
        render_frame(impl, window, jb, machines)

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    start_gui(
        {('127.0.0.1', 54686): {'cpu': 66.7, 'ram': 45.4, 'name': 'DESKTOP-E17Q9F2', 'cores': 12,
                                'ip': '192.168.0.121'},
         ('127.0.0.1', 541241): {'cpu': 66.7, 'ram': 45.4, 'name': 'DESKTOP-E17Q9F2', 'cores': 12,
                                 'ip': '192.168.0.121'},
         ('127.0.0.1', 541123241): {'cpu': 66.7, 'ram': 45.4, 'name': 'DESKTOP-E17Q9F2', 'cores': 12,
                                    'ip': '192.168.0.121'}}
    )
