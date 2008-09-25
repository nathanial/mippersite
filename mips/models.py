from django.db import models

class UserProgram(models.Model):
    name = models.CharField(maxlength=30, unique=True)
    code = models.TextField()
    def __cmp__(self, other):
        if self.name > other.name:
            return 1
        elif self.name == other.name:
            return 0
        else:
            return -1

