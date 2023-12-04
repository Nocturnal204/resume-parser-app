from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from .models import ParsedResume
from rp_app.resume_parser import parse_resume

# Create your views here.

def index (request):
    # Get last 10 uploaded resumes from database
    resumes = ParsedResume.objects.all().order_by('-id')[:10]
    context = {
        'title': 'Resume Parser Data',
        'resumes': resumes
    }
    return render(request, 'index.html', context)

def upload(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            parsed_data = parse_resume(resume_file)
            ParsedResume.objects.create(
                name=parsed_data['name'],
                email=parsed_data['email'],
                mobile=parsed_data['mobile'],
                education=parsed_data['education'],
                skills=parsed_data['skills'],
                resume=resume_file
            )
            # Retun redirect to index page with success message
            return redirect('index')
    else:
        form = ResumeUploadForm()
    return render(request, 'upload.html', {'form': form, 'title': 'Upload Resume'})

def delete(request, id):
    # Get resume object by id
    resume_data = ParsedResume.objects.get(id=id)
    # Delete resume file from media/resume_files
    resume_data.resume.delete()
    # Delete resume object
    resume_data.delete()
    # Return redirect to index page with success message
    return redirect('index')