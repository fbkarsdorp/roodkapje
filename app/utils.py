
class SectionCounter(object):
    def __init__(self, max_depth=5):
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