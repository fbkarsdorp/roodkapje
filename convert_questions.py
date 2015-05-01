import codecs

class SectionCounter(object):
    def __init__(self, max_depth=10):
        self.section_counts = [0] * max_depth
        self.max_depth = max_depth
        self.last_marker = 0

    def _update_counts(self, marker):
        marker_count = marker.count('#')
        self.section_counts[marker_count - 1] += 1
        if marker_count - self.last_marker > 1:
            raise ValueError("Number level skipped...")
        if marker_count < self.last_marker:
            for i in range(marker_count, self.max_depth):
                self.section_counts[i] = 0
        self.last_marker = marker_count

    def to_number(self, marker):
        self._update_counts(marker)
        return '.'.join(str(c) for c in self.section_counts if c > 0)

if __name__ == '__main__':
    sc = SectionCounter()
    with codecs.open("questions.csv", 'w', 'utf-8') as outfile:
        for k, line in enumerate(codecs.open("schema.md", encoding='utf-8')):
            fields = line.strip().split('\t')
            if len(fields) > 1:
                qnumber = sc.to_number(fields[0])
            if len(fields) <= 2:
                continue
            if fields[1] == 'B':
                qtype, question, options, default = fields[1], fields[2], 'ja,nee', 'nee'
            elif fields[1] == 'R':
                qtype, question, options = fields[1], fields[2], [f.strip() for f in fields[3].split(',')]
                default = options[0]
                options = ','.join(options)#next(option for option in options if option.startswith('*'))
            elif fields[1] == 'T':
                qtype, question, options, default = fields[1], fields[2], None, '-'
            else:
                raise ValueError("Unsupported question type.")
            outfile.write(u"{qnumber};{qtype};{question};{options};{default}\n".format(
                qnumber=qnumber, qtype=qtype, question=question, options=options if options else '', default=default))

    
