from flask import Flask, render_template, request, redirect, url_for
import random
import csv
import os


## Read information
def read_info():
    ##get current absolute directly of file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "static/subjects.csv")
    rows = []
    with open(filename, "r") as f:
        csvreader = csv.reader(f)
        next(csvreader)
        for row in csvreader:
            rows.append(row)
    return rows

subject_info = read_info()

app = Flask(__name__)

## flask routing functions
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/see_csv/')
def see_csv():
    return render_template('see_csv.html', subject_info=subject_info)

@app.route('/opt_subjs/')
def opt_subjs():
    import copy
    subj_info = copy.deepcopy(subject_info)
    level = request.args['year']
    if level in "12":
        ## if is sec 1 or 2, go directly to score page
        return redirect(url_for('process_results', level=level))
    ## else sec 3 or 4 would need to select subjects
    compul_subjs = []
    opt_sci_subjs = []
    opt_hums_subjs = []

    for subj in subj_info:
        if level in subj[3] and subj[4] == "T":
            if subj[0] == "CID":
                subj[0] = "CID" + str(level)
                if level == "4":
                    subj[0] += "+"
            compul_subjs.append(subj)
        elif level in subj[3] and subj[4] == "F":
            if subj[2] == "Science":
                opt_sci_subjs.append(subj)
            elif subj[2] == "Humanities":
                opt_hums_subjs.append(subj)
    return render_template('opt_subjs.html', compul_subjs=compul_subjs, 
    opt_sci_subjs=opt_sci_subjs, opt_hums_subjs=opt_hums_subjs, level=level)

@app.route('/process_results/', methods=["GET", "POST"])
def process_results():
    ## function to process get and post requests
    import copy
    subj_info = copy.deepcopy(subject_info)
    all_subjs = []
    if request.method=="GET":
        #go to enter score page
        level = request.args['level']
        print("(process_results) User is year ", level)
        if level in "12":
            for subj in subj_info:
                if level in subj[3]:
                    if subj[0] == "CID":
                            subj = [("CID" + str(level)), subj[0]]
                            #("CID IS ", subj[0])
                    all_subjs.append(subj)

            for subj in all_subjs:
                subj.append(random.randint(30, 100))


            return render_template('score.html', 
                            all_subjs=all_subjs, 
                            level=level)
    else:
        #go to enter result page (private)
        if level in "34":
            sci_subjs = request.args.getlist("opt_sci_subj")
            hums_subjs = request.args.getlist("opt_hums_subj")
            #print(sci_subjs, hums_subjs)
            for subj in subj_info:
                if level in subj[3] and subj[4] == "T":
                    if subj[0] == "CID":
                        subj[0] = "CID" + str(level)
                        if level == "4":
                            subj[0] += "+"
                    all_subjs.append(subj)
                elif subj[1] in sci_subjs or subj[1] in hums_subjs:
                    all_subjs.append(subj)

            for subj in all_subjs:
                subj.append(random.randint(30, 100))


            return render_template('score.html', 
                            all_subjs=all_subjs, 
                            level=level,
                            sci_subjs=sci_subjs,
                            hums_subjs=hums_subjs)

@app.route('/result/')#, methods=["POST"])
def result():
    year = request.args['year']
    print("IN result: YEAR=", year)
    user_scores = request.args.getlist("grade")
    user_subjs = request.args.getlist("subject")
    #print(request.args)
    #print(user_subjs)
    #grades = []
    grade_and_subj = []
    for i in range(len(user_scores)):
        #print(score)
        subject_grade = []
        subject_grade.append(user_scores[i])
        subject_grade.append(score_to_grade(int(user_scores[i])))
        subject_grade.append(user_subjs[i])
        grade_and_subj.append(subject_grade)
        #grades.append(score_to_grade(int(user_scores[i])))
        #user_subjs = user_subjs[(user_scores.index(score)+1):]

    #( "Grade n scores: ",grade_and_subj)

    if year in "12":
        gpa=calc_GPA(grade_and_subj, year)
        gpa=round(gpa, 2)
        for item in grade_and_subj:
            item.append(grade_to_gpa(item[1]))
        return render_template('result.html', 
                                gpa=gpa, 
                                grade_and_subj=grade_and_subj, 
                                user_subjs=user_subjs, 
                                level=year,
                                year4=False)

    elif year == "3":
        sci_subjs = request.args.getlist("opt_sci_subj")
        hums_subjs = request.args.getlist("opt_hums_subj")
        gpa=calc_GPA(grade_and_subj, year)[0]
        gpa=round(gpa, 2)
        subjects_counted_in_gpa = calc_GPA(grade_and_subj, year)[1]
        for item in grade_and_subj:
            item.append(grade_to_gpa(item[1]))
            if item in subjects_counted_in_gpa:
                item.append("counted")

        print("list to pass through to result page: ", grade_and_subj)
        #print("y3 user subjs: ", user_subjs)
        return render_template('result.html', 
                                 gpa=gpa, 
                                 grade_and_subj=grade_and_subj, 
                                 user_subjs=user_subjs, 
                                 level=year, 
                                 sci_subjs=sci_subjs,
                                 hums_subjs=hums_subjs,
                                 year4=True)

    elif year == "4":
        sci_subjs = request.args.getlist("opt_sci_subj")
        hums_subjs = request.args.getlist("opt_hums_subj")
        gpa=calc_GPA(grade_and_subj, year)[0]
        math_double_count=calc_GPA(grade_and_subj, year)[2]
        subjs_counted=calc_GPA(grade_and_subj, year)[1]
        gpa=round(gpa, 2)

        for item in grade_and_subj:
            item.append(grade_to_gpa(item[1]))
            if item[2] == "Mathematics":
                if math_double_count:
                    #print("MAth is double")
                    item.append("double")
                else:
                    item.append("counted")
            elif item in subjs_counted:
                item.append("counted")
            else:
                item.append("not_counted")

        print("list to pass through to result page: ", grade_and_subj)
        return render_template('result.html',
                                 gpa=gpa, 
                                 grade_and_subj=grade_and_subj, 
                                 user_subjs=user_subjs, 
                                 sci_subjs=sci_subjs,
                                 hums_subjs=hums_subjs,
                                 level=year, 
                                 year4=True)


def calc_GPA(grades, year):
    print("IN GPA: year = ", year)
    print("Grades in calc gpa: ", grades)
    result = 0
    gpa_dict = {"A1*":5, "A1":4, "A2":3.5, "B3":3, "B4":2.5, "C5":2, "C6":1.5, "D7":1, "E8":0.5, "F9":0}

    sci_subs = []
    hum_subs = []
    compul_subs = []

    for pair in grades:
        if pair[2] == "Computing" or pair[2] == "Physics" or pair[2] == "Biology" or pair[2] == "Chemistry":
            sci_subs.append(pair)
        elif pair[2] == "History" or pair[2] == "Geography" or pair[2] == "English Literature" or pair[2] == "Chinese Literature" or pair[2] == "Bicultural Studies Programme" or (pair[2] == "Singapore Studies" and year=="4"):
            hum_subs.append(pair)
        else:
            compul_subs.append(pair)

    if year in "12":
        for grade in grades:
            result += gpa_dict[grade[1]]
        return (result/len(grades))

    elif year == "3":
        best_hum = sorted(hum_subs)[-1]
        best_scis = sorted(sci_subs)[1:]
        subjects_counted_in_gpa = [best_hum]
        print("BEST HUMANS AND SCI",best_hum, best_scis)
        for subj in compul_subs:
            if subj[1] == "Maths":
                result += gpa_dict[subj[1]]*2
            elif subj[1] == "Singapore Studies":
                result += gpa_dict[subj[1]]*0.5
                subjects_counted_in_gpa.append(subj)
            else:
                result += gpa_dict[subj[1]]
            subjects_counted_in_gpa.append(subj)
        result += gpa_dict[best_hum[1]]
        
        for sci in best_scis:
            result += gpa_dict[sci[1]]
            subjects_counted_in_gpa.append(sci)
        
        return [(result/8), subjects_counted_in_gpa]

    elif year == "4":
        #print(sorted(hum_subs))
        best_hum = sorted(hum_subs)[-1]
        best_sci = sorted(sci_subs)[-1]
        subjects_counted_in_gpa = [best_hum, best_sci]
        print("BEST HUMANS AND SCI",best_hum, best_sci)
        for subj in compul_subs:
            subjects_counted_in_gpa.append(subj)
            result += gpa_dict[subj[1]]
        result += gpa_dict[best_hum[1]]
        result += gpa_dict[best_sci[1]]

        other_subjs = []
        for subj in grades:
            #print(subj[2])
            #print(subj not in best_hum)
            #print(subj not in best_sci)
            #print(subj not in compul_subs)
            if (subj != best_hum and subj != best_sci and subj not in compul_subs) or subj[2] == "Mathematics":
                other_subjs.append(subj)

        print("other subjs", sorted(other_subjs))
            
        best_2_subj = [sorted(other_subjs)[-2]] + [sorted(other_subjs)[-1]]
        print("BEST other 2",best_2_subj)
        for subj in best_2_subj:
            result += gpa_dict[subj[1]]
            subjects_counted_in_gpa.append(subj)

        math_count = 0
        math_double_count = False
        for subj in subjects_counted_in_gpa:
            if subj[2] == "Mathematics":
                #print("hi math")
                math_count += 1

        print("Subjs counted: ", subjects_counted_in_gpa)
        #print(f"There are {math_count} math")

        if math_count == 2:
            math_double_count = True

        #print("double math? ", math_double_count)
        return [(result/8), subjects_counted_in_gpa, math_double_count]

def score_to_grade(score):
    pairs = [[85, "A1*"], [75, "A1"], [70, "A2"], [65, "B3"], [60, "B4"], [55, "C5"], [45, "D7"], [40, "E8"], [0, "F9"]]
    for pair in pairs:
        if score>=pair[0]:
            grade=pair[1]
            return grade

def grade_to_gpa(grade):
    gpa_dict = {"A1*":5, "A1":4, "A2":3.5, "B3":3, "B4":2.5, "C5":2, "C6":1.5, "D7":1, "E8":0.5, "F9":0}
    return gpa_dict[grade]

## run app
if __name__ == '__main__':
    app.run(debug=True)