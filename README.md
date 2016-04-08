# pkgbuilder
PKGBUILD builder for Arch linux User repository

Written in Python 3. Based on PKGBUILD templates provided by `pacman`.

## USAGE

```
USAGE:
 * ./pkgman nodejs package_name
 * ./pkgman ruby package_name
 * ./pkgman python package_name
```

## DEPENDENCIES

This script uses [the Jinja2 template engine](http://jinja.pocoo.org/) to
generate PKGBUILD scripts. You can install it from the Arch linux repos:

```sh
sudo pacman -Sy python-jinja
```

## EXAMPLES

For example, we want to generate a PKGBUILD script for the Rails Ruby Gem
```sh
./pkgbuilder ruby rails
```

Produces this PKGBUILD script

```sh
# Generated on: Fri Apr  8 23:41:06 2016
# Maintainer: Your Name <your email at example dot com>

_gemname=rails
pkgname=ruby-${_gemname//_/-}
pkgver=4.2.6
pkgrel=1
pkgdesc="Ruby on Rails is a full-stack web framework optimized for programmer happiness and sustainable productivity. It encourages beautiful code by favoring convention over configuration."
arch=(any)
url="http://www.rubyonrails.org"
license=('MIT' )
depends=('ruby'
        'ruby-actionmailer'
        'ruby-actionpack'
        'ruby-actionview'
        'ruby-activejob'
        'ruby-activemodel'
        'ruby-activerecord'
        'ruby-activesupport'
        'ruby-bundler'
        'ruby-railties'
        'ruby-sprockets-rails')
makedepends=('rubygems')
source=(http://gems.rubyforge.org/gems/$_gemname-$pkgver.gem)
noextract=($_gemname-$pkgver.gem)
sha256sums=('a199258c0d2bae09993a6932c49df254fd66428899d1823b8c5285de02e5bc33')

package() {
  cd "$srcdir"
  # _gemdir is defined inside package() because if ruby[gems] is not installed on
  # the system, makepkg will exit with an error when sourcing the PKGBUILD.
  local _gemdir="$(ruby -rubygems -e'puts Gem.default_dir')"

  gem install --no-user-install --ignore-dependencies -i "$pkgdir$_gemdir" -n "$pkgdir/usr/bin" \
    "$_gemname-$pkgver.gem"
}

# vim:set ts=2 sw=2 et:
```
