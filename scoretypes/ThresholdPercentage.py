from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from future.builtins import *  # noqa
from future.builtins.disabled import *  # noqa
from six import iterkeys, itervalues

from cms.grading.scoretypes import ScoreTypeAlone


# Dummy function to mark translatable string.
def N_(message):
    return message


class ThresholdPercentage(ScoreTypeAlone):
    """If T is the number of test cases, C the number of correct testcases and p the threshold parameter,
    the score of a submission is max((C - p * T) / (T - p * T) * 100, 0) """
    # Mark strings for localization.
    N_("#")
    N_("Outcome")
    N_("Details")
    N_("Execution time")
    N_("Memory used")
    N_("N/A")
    TEMPLATE = """\
<table class="testcase-list">
    <thead>
        <tr>
            <th class="idx">
                {% trans %}#{% endtrans %}
            </th>
            <th class="outcome">
                {% trans %}Outcome{% endtrans %}
            </th>
            <th class="details">
                {% trans %}Details{% endtrans %}
            </th>
    {% if feedback_level == FEEDBACK_LEVEL_FULL %}
            <th class="execution-time">
                {% trans %}Execution time{% endtrans %}
            </th>
            <th class="memory-used">
                {% trans %}Memory used{% endtrans %}
            </th>
    {% endif %}
        </tr>
    </thead>
    <tbody>
    {% for tc in details %}
        {% if "outcome" in tc and "text" in tc %}
            {% if tc["outcome"] == "Correct" %}
        <tr class="correct">
            {% elif tc["outcome"] == "Not correct" %}
        <tr class="notcorrect">
            {% else %}
        <tr class="partiallycorrect">
            {% endif %}
            <td class="idx">{{ loop.index }}</td>
            <td class="outcome">{{ _(tc["outcome"]) }}</td>
            <td class="details">{{ tc["text"]|format_status_text }}</td>
            {% if feedback_level == FEEDBACK_LEVEL_FULL %}
            <td class="execution-time">
                {% if tc["time"] is not none %}
                {{ tc["time"]|format_duration }}
                {% else %}
                {% trans %}N/A{% endtrans %}
                {% endif %}
            </td>
            <td class="memory-used">
                {% if tc["memory"] is not none %}
                {{ tc["memory"]|format_size }}
                {% else %}
                {% trans %}N/A{% endtrans %}
                {% endif %}
            </td>
            {% endif %}
        {% else %}
        <tr class="undefined">
            <td colspan="5">
                {% trans %}N/A{% endtrans %}
            </td>
        </tr>
        {% endif %}
    {% endfor %}
    </tbody>
</table>"""

    @property
    def threshold(self):
        return self.parameters

    def max_scores(self):
        """See ScoreType.max_score."""
        return 100, 100, []

    def compute_score(self, submission_result):
        """See ScoreType.compute_score."""
        # Actually, this means it didn't even compile!
        if not submission_result.evaluated():
            return 0.0, [], 0.0, [], []

        # XXX Lexicographical order by codename
        indices = sorted(iterkeys(self.public_testcases))
        evaluations = dict((ev.codename, ev) for ev in submission_result.evaluations)
        testcases = []
        public_testcases = []

        C = 0
        for idx in indices:
            outcome = float(evaluations[idx].outcome)
            testcases.append({
                "idx": idx,
                "outcome": self.get_public_outcome(outcome),
                "text": evaluations[idx].text,
                "time": evaluations[idx].execution_time,
                "memory": evaluations[idx].execution_memory,
            })
            C += outcome > 0
            if self.public_testcases[idx]:
                public_testcases.append(testcases[-1])
            else:
                public_testcases.append({"idx": idx})

        p = self.threshold
        T = len(testcases)
        score = max(0, (C - p * T) / (T - p * T) * 100)

        return score, testcases, score, public_testcases, []

    def get_public_outcome(self, outcome):
        """Return a public outcome from an outcome.
        outcome (float): the outcome of the submission.
        return (float): the public output.
        """
        if outcome > 0.0:
            return N_("Correct")
        else:
            return N_("Not correct")
