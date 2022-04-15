class Wealth:

    cp = 0
    sp = 0
    ep = 0
    gp = 0
    pp = 0

    def __init__(self, cp, sp, ep, gp, pp):
        self.cp = cp
        self.sp = sp
        self.ep = ep
        self.gp = gp
        self.pp = pp

    # def convert(self):

    def addCp(self, cp):
        self.cp = self.cp + cp

    def addSp(self, sp):
        self.sp = self.sp + sp

    def addEp(self, ep):
        self.ep = self.ep + ep

    def addGp(self, gp):
        self.gp = self.gp + gp

    def addPp(self, pp):
        self.pp = self.pp + pp

    def rmCp(self, cp):
        self.cp = self.cp - cp

    def rmSp(self, sp):
        self.sp = self.sp - sp

    def rmEp(self, ep):
        self.ep = self.ep - ep

    def rmGp(self, gp):
        self.gp = self.gp - gp

    def rmPp(self, pp):
        self.pp = self.pp - pp
