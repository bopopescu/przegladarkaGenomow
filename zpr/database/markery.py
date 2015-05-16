#TODO class Markery
from dbbase import DBBase
from zprapp.models import Organism, Meaning, Marker
import psycopg2
import psycopg2.extras

class Markery(DBBase):
    def glos(self):
        print 'Markery! '

    def create(self):
        #wszystkie markery tworze jako atrapy dla pierwszego chromosomu
        #jaki jest w bazie (czyli dla pierwszego organizmu) z losowym znaczeniem
        NAME = ["SR123", "SF35324", "SQ54353", "SJ432", "SP5435"]
        START = [10, 10000, 100000, 1000000, 10000000]
        LENGTH = [5000, 15000, 150000, 1500000, 15000000]
        MEANING = Meaning.objects.all()[:2]
        org = Organism.objects.all()[0];
        chr = org.chromosome_set.all()[0];
        for i in range(NAME.__len__()):
            if(i%2):
                m = MEANING[0]
            else:
                m = MEANING[1]
            marker = Marker(chromosome = chr, name = NAME[i], start = START[i], length = LENGTH[i], meaning = m)
            marker.save();
            #chr.marker_set.create(name = NAME[i], start = START[i], length = LENGTH[i], meaning = m);
        print "utworzono markery";

    def delete(self):
        markers = Marker.objects.all()
        for m in markers:
            m.delete();
        print "usunieto markery";

    def get_good_bad_undef_data(self):
        # porownuje markery z xls i ich przynaleznosci ze scaffoldami z bazy backupu init
        # i zwraca poprawne, niepoprawne oraz niezdefiniowane
        markers = self._get_data_from_xls()
        NAME, SC_ID, START, STOP = 1, 6, 7, 8;
        markers = [(int(d[0]), d[NAME], d[2], int(d[3]), int(d[4]), int(d[5]), int(d[SC_ID]), int(d[START]), int(d[STOP])) for d in markers]
        scflds = self._get_data_without_bad_id()
        ID, LENGTH_BP, ASSEMB_TYPE = 0, 1, 2;
        scflds_id = [sc[ID] for sc in scflds]
        scflds_length = [sc[LENGTH_BP] for sc in scflds]
        scflds_assemb_type = [sc[ASSEMB_TYPE] for sc in scflds]
        good_markers=[]
        bad_markers=[]
        undef_markers=[]
        for marker in markers:
            if marker[SC_ID] not in scflds_id:
                undef_markers.append((marker[NAME], marker[SC_ID]))
                continue;
            else:
                index = scflds_id.index(marker[SC_ID],)
                sc_len = scflds_length[index]
                sc_assemb_type = scflds_assemb_type[index]
                if sc_len < marker[START] or sc_len < marker[STOP]:
                    bad_markers.append({'name':marker[NAME], 'sc_id':marker[SC_ID], 'sc_len':sc_len, 'start':marker[START], 'stop':marker[STOP] ,'assemb_type':sc_assemb_type})
                else:
                    good_markers.append({'name':marker[NAME], 'sc_id':marker[SC_ID], 'sc_len':sc_len, 'start':marker[START], 'stop':marker[STOP] ,'assemb_type':sc_assemb_type})
        return good_markers, bad_markers, undef_markers

    def _get_data_from_xls(self):
        import xlrd;
        workbook = xlrd.open_workbook(self.MARKER_FILE_LOCATION);
        sheet = workbook.sheet_by_index(1);
        # for row in range(2, sheet.nrows):
        #     print sheet.cell_value(0, row)
        data = [[sheet.cell_value(r,c) for c in range(sheet.ncols)] for r in range(2, sheet.nrows)]
        #data = [(int(d[0]), d[1], d[2], int(d[3]), int(d[4]), int(d[5]), int(d[6]), int(d[7]), int(d[8])) for d in data]
        return data

    def _get_data_without_bad_id(self):
        #takie scaffoldy ktore nie maja liter w id
        ID, LENGTH_BP, ASSEMB_TYPE = 0, 1, 2
        try:
            conn = psycopg2.connect(self.CONNECT_STRING)
        except:
            print "CONNECT DATABASE ERROR"
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select id, length_bp, assemb_type from scaffold_scaffold")
        data = cur.fetchall()
        scflds=[]
        for sc in data:
            try:
                scflds.append((int(sc[ID]), int(sc[LENGTH_BP]), sc[ASSEMB_TYPE]))
            except:
                continue;
        return scflds;

    def _get_data_with_bad_text_id(self):
        #sprawdza czy w id scaffolda nie ma np liter
        try:
            conn = psycopg2.connect(self.CONNECT_STRING)
        except:
            print "CONNECT DATABASE ERROR"
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select id, assemb_type from scaffold_scaffold")
        rows = cur.fetchall()
        bad_id = []
        for row in rows:
            try:
                id = row['id']
                int(id)
            except ValueError:
                bad_id.append((id, row['assemb_type']))
        return bad_id;
