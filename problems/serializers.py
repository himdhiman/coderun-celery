from django.db.models import fields
from rest_framework import serializers
from problems import models
from core.helper import decode_data

class TagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = models.Tag
        fields = '__all__'

class TagSerializerCreateProblem(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = models.Tag
        fields = '__all__'
    def to_representation(self, obj):
        primitive_repr = super(TagSerializerCreateProblem, self).to_representation(obj)
        primitive_repr['value'] = primitive_repr['id']
        return primitive_repr 

class ProblemListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    class Meta:
        model = models.Problem
        fields = ['id', 'title', 'tags', 'totalSubmissions', 'problem_level']

    def to_representation(self, obj):
        primitive_repr = super(ProblemListSerializer, self).to_representation(obj)
        primitive_repr['solved'] = "Unsolved"
        return primitive_repr 

class ProblemListStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Problem
        fields = ['id']

    def to_representation(self, obj):
        primitive_repr = super(ProblemListStatusSerializer, self).to_representation(obj)
        mail_id = self.context.get("mail_id")
        if mail_id:
            data = models.Submission.objects.filter(problem_Id = obj.id, 
                created_By = mail_id).order_by("-score")
            if len(data) > 0:
                data = data.first()
                if data.score == data.total_score:
                    primitive_repr['solved'] = "Solved"
                else:
                    primitive_repr['solved'] = "Attempted"
                return primitive_repr 
        primitive_repr['solved'] = "Unsolved"
        return primitive_repr

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Problem
        fields = [
            'created_by', 
            'title', 
            'note', 
            'problem_statement', 
            'input_format', 
            'constraints', 
            'output_format', 
            'tags', 
            'problem_level', 
            'time_Limit', 
            'memory_Limit'
        ]

class GetProblemSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    class Meta:
        model = models.Problem
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = '__all__'

class SubmissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = [
            'language',
            'status',
            'score',
            'total_score',
            'submission_Date_Time'
        ]

class AllSubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = [
            'problem_Id',
            'language',
            'status',
            'score',
            'total_score',
            'submission_Date_Time'
        ]

class EditorialSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = models.Editorial
        fields = '__all__'



class SavedCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SavedCode
        fields = ["code", "language", "submission_Date_Time"]

    def to_representation(self, obj):
        primitive_repr = super(SavedCodeSerializer, self).to_representation(obj)
        primitive_repr['code'] = decode_data(obj.code)
        return primitive_repr