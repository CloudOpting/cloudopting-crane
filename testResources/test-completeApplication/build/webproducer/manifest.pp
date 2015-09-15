# Clone repo
vcsrepo { '/usr/src/app':
  ensure   => present,
  provider => git,
  source   => 'git://github.com/wtelecom/crane-tests-webproducer.git',
}

# Install requirements

class { 'python' :
  version    => 'system',
  pip        => 'present',
  dev        => 'present',
}

python::requirements { '/usr/src/app/requirements.txt' :
  owner      => 'root',
}
