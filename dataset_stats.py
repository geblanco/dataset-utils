#!/usr/bin/env python3
import argparse
import json
import sys

flags = None

def parse_flags():
  parser = argparse.ArgumentParser()
  parser.add_argument('data', nargs='*', help='Datasets to get stats from')
  parser.add_argument('--format', '-f', default='race', help='Format of the'
      'datasets to get staats (default RACE like format)')
  parser.add_argument('--stats', '-s', action='store_true', help='Just get'
      'basic stats of each dataset')
  parser.add_argument('--clean', '-c', action='store_true', help='Whether to'
      'clean tasks with more options than n_options')
  parser.add_argument('--n_options', '-n', default=-1, type=int, help='Remove tasks with'
      'options different from this parameter')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  return parser.parse_args()

def race_stats(dataset):
  n_tasks = len(dataset)
  questions_per_task = [len(d['questions']) for d in dataset]
  avg_questions_per_task = sum(questions_per_task)/n_tasks
  nof_options_per_task = [len(d['options'][0]) for d in dataset]
  avg_nof_options_per_task = sum(nof_options_per_task)/n_tasks
  return {
    'Number of tasks': n_tasks,
    'Avg questions per task':avg_questions_per_task,
    'Avg options per task':avg_nof_options_per_task,
  }

def print_stats(stats):
  for key in stats.keys():
    print('\t{}: {}'.format(key, stats[key]))

def load_data(paths):
  datasets = []
  for path in paths:
    data = json.load(open(path, 'r'))['data']
    datasets.append(data)
  return datasets

def stats(datasets):
  check_format(flags.format)
  stats_fn = formats[flags.format]
  for path, dataset in datasets:
    print(path)
    print_stats(stats_fn(dataset))

def write_dataset(path, dataset):
  data = json.load(open(path, 'r'))
  data['data'] = dataset
  json.dump(fp=open(path, 'w'), obj=data, ensure_ascii=False)

def clean_dataset(path, dataset, n_options):
  tasks = []
  for task in dataset:
    if len(task["options"][0]) == n_options:
      tasks.append(task)
  if len(tasks) == 0:
    print('Dataset {} got empty, leaving dataset as is'.format(path))
    tasks = dataset
  return tasks

def clean(datasets, n_options):
  for path, dataset in datasets:
    cleaned = clean_dataset(path, dataset, n_options)
    write_dataset(path, cleaned)    

def check_format(fmt):
  available_formats = list(formats.keys())
  if fmt not in available_formats:
    raise ValueError('Format must be one of: {}'.format(', '.join(available_formats)))

formats = {
  'race': race_stats
}

if __name__ == '__main__':
  flags = parse_flags()
  if flags.stats or flags.clean:
    datasets = list(zip(flags.data, load_data(flags.data)))
    if flags.stats:
      stats(datasets)
    if flags.clean and flags.n_options != -1:
      clean(datasets, flags.n_options)
      datasets = list(zip(flags.data, load_data(flags.data)))
      stats(datasets)
