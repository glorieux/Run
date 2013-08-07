import os
import sublime
import sublime_plugin
import subprocess
import threading, queue

class Runner(threading.Thread):
  def __init__(self, command, shell, env, view):
    self.stdout = None
    self.stderr = None
    self.command = command or ''
    self.shell = shell or ''
    self.env = env or ''
    self.view = view or None
    threading.Thread.__init__(self)

  def run(self):
    proc = subprocess.Popen(
      [self.shell, '-ic', self.command],
      shell=False,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      universal_newlines=True,
      env=self.env
    )

    self.stdout, self.stderr = proc.communicate()
    self.view.run_command('insert_view', { 'string': self.stdout })

class RunCommand(sublime_plugin.WindowCommand):
  def run(self):
    input_view = self.window.show_input_panel('Run:', '', self.user_input, None, None)
    input_view.set_read_only(False)
    input_view.set_name('run_input_view')
    input_view.run_command('insert_input_panel_text', { 'string': '\n' })
    input_view.show(1)

  def user_input(self, input):
    input = input.strip('\n')
    hist_file_path = os.path.dirname(os.path.abspath(__file__)) + '/.run_history'
    hist_file = open(hist_file_path, 'a+')
    hist_file.write(input + '\n')
    view = self.window.new_file()

    view.set_scratch(True)
    view.set_name('Run: ' + input.split()[0])
    view.run_command('insert_view', { 'string': 'Running: ' + input + '\n' })

    runner = Runner(input, os.environ['SHELL'], os.environ.copy(), view)
    runner.start()


class InsertViewCommand(sublime_plugin.TextCommand):
  def run(self, edit, string=''):
    self.view.set_read_only(False)
    self.view.insert(edit, self.view.size(), string)
    self.view.set_read_only(True)

class InsertInputPanelTextCommand(sublime_plugin.TextCommand):
  def run(self, edit, string = ''):
    self.view.erase(edit, self.view.line(0))
    self.view.erase(edit, self.view.full_line(1))
    self.view.insert(edit, 0, string)

class Events(sublime_plugin.EventListener):
  def __init__(self):
    self.hist_file_path = os.path.dirname(os.path.abspath(__file__)) + '/.run_history'
    self.hist_file = list(open(self.hist_file_path, 'r'))
    self.hist_file.reverse()
    self.count = 0

  def on_text_command(self, view, command_name, args):
    if command_name == 'move' and args['forward'] == False and args['by'] == 'lines':
      if view.name() == 'run_input_view' and self.count < len(self.hist_file):
        view.run_command('insert_input_panel_text', { 'string': '\n' + self.hist_file[self.count].strip('\n') })
        self.count += 1
