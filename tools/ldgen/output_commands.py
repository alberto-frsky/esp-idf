#
# Copyright 2021 Espressif Systems (Shanghai) CO LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from entity import Entity


class AlignAtAddress():

    def __init__(self, alignment):
        self.alignment = alignment

    def __str__(self):
        return ('. = ALIGN(%d);' % self.alignment)

    def __eq__(self, other):
        return (isinstance(other, AlignAtAddress) and
                self.alignment == other.alignment)


class SymbolAtAddress():

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return ('%s = ABSOLUTE(.);' % self.symbol)

    def __eq__(self, other):
        return (isinstance(other, SymbolAtAddress) and
                self.symbol == other.symbol)


class InputSectionDesc():

    def __init__(self, entity, sections, exclusions=None, keep=False, sort=None):
        assert(entity.specificity != Entity.Specificity.SYMBOL)

        self.entity = entity
        self.sections = set(sections)

        self.exclusions = set()

        if exclusions:
            assert(not [e for e in exclusions if e.specificity == Entity.Specificity.SYMBOL or
                        e.specificity == Entity.Specificity.NONE])
            self.exclusions = set(exclusions)
        else:
            self.exclusions = set()

        self.keep = keep
        self.sort = sort

    def __str__(self):
        sections_string = '( )'

        if self.sections:
            exclusion_strings = []

            for exc in sorted(self.exclusions):
                if exc.specificity == Entity.Specificity.ARCHIVE:
                    exc_string = '*%s' % (exc.archive)
                else:
                    exc_string = '*%s:%s.*' % (exc.archive, exc.obj)

                exclusion_strings.append(exc_string)

            section_strings = []

            if exclusion_strings:
                exclusion_string = 'EXCLUDE_FILE(%s)' % ' '.join(exclusion_strings)

                for section in sorted(self.sections):
                    section_strings.append('%s %s' % (exclusion_string, section))
            else:
                for section in sorted(self.sections):
                    section_strings.append(section)

            if self.sort:
                if self.sort == (None, None):
                    pattern = 'SORT(%s)'
                elif self.sort == ('name', None):
                    pattern = 'SORT_BY_NAME(%s)'
                elif self.sort == ('alignment', None):
                    pattern = 'SORT_BY_ALIGNMENT(%s)'
                elif self.sort == ('init_priority', None):
                    pattern = 'SORT_BY_INIT_PRIORITY(%s)'
                elif self.sort == ('name', 'alignment'):
                    pattern = 'SORT_BY_NAME(SORT_BY_ALIGNMENT(%s))'
                elif self.sort == ('alignment', 'name'):
                    pattern = 'SORT_BY_ALIGNMENT(SORT_BY_NAME(%s))'
                elif self.sort == ('name', 'name'):
                    pattern = 'SORT_BY_NAME(SORT_BY_NAME(%s))'
                elif self.sort == ('alignment', 'alignment'):
                    pattern = 'SORT_BY_ALIGNMENT(SORT_BY_ALIGNMENT(%s))'
                else:
                    raise Exception('Invalid sort arguments')

                section_strings = [(pattern % s) for s in section_strings]

            sections_string = '(%s)' % ' '.join(section_strings)

        if self.entity.specificity == Entity.Specificity.NONE:
            entry = '*%s' % (sections_string)
        elif self.entity.specificity == Entity.Specificity.ARCHIVE:
            entry = '*%s:%s' % (self.entity.archive, sections_string)
        else:
            entry = '*%s:%s.*%s' % (self.entity.archive, self.entity.obj, sections_string)

        if self.keep:
            res = 'KEEP(%s)' % entry
        else:
            res = entry

        return res

    def __eq__(self, other):
        return (isinstance(other, InputSectionDesc) and
                self.entity == other.entity and
                self.sections == other.sections and
                self.exclusions == other.exclusions and
                self.keep == other.keep and
                self.sort == other.sort)
