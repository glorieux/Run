import sublime, sublime_plugin
import subprocess
import os
import threading

class Runner(threading.Thread):
    def __init__(self, command, shell, env, view):
      self.stdout = None
      self.stderr = None
      self.command = command or ''
      self.shell = shell or ''
      self.env = env or ''
      self.view = view or None
      threading.Thread.__init__(self, daemon=True)

    def run(self):
      proc = subprocess.Popen(
        [self.shell, '-ic', self.command],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=self.env
      )

      while True:
        out = proc.stdout.read(1)
        if out == '' and proc.poll() != None:
          break
        if out != '':
          self.view.run_command('insert_view', { 'string': out })

class RunCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.show_input_panel('Run:', '', self.user_input, None, None)

  def user_input(self, stri):
    view = self.window.new_file()

    view.set_scratch(True)
    view.set_name('Run: ' + stri.split()[0])
    view.run_command('insert_view', { 'string': 'Running: ' + stri + '\n' })

    runner = Runner(stri, os.environ['SHELL'], os.environ.copy(), view)
    runner.start()

class InsertViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, string=''):
      self.view.set_read_only(False)
      self.view.insert(edit, self.view.size(), string)
      self.view.set_read_only(True)

