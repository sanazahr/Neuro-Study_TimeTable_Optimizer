"""
AI Quiz Question Generator
Generates practice questions based on subject names and topics
"""

import random
import re

class QuizGenerator:
    """Generates intelligent quiz questions from subject names"""
    
    # Question templates for different subject types
    QUESTION_TEMPLATES = {
        'coding': [
            {"template": "What is the time complexity of {topic}?", "type": "complexity"},
            {"template": "Explain the difference between {topic1} and {topic2}.", "type": "compare"},
            {"template": "Write a simple code example for {topic}.", "type": "code"},
            {"template": "What are the advantages and disadvantages of {topic}?", "type": "analysis"},
            {"template": "How does {topic} work internally?", "type": "explanation"}
        ],
        'theory': [
            {"template": "Define {topic} in your own words.", "type": "definition"},
            {"template": "What are the key concepts of {topic}?", "type": "concepts"},
            {"template": "Explain the importance of {topic} in computer science.", "type": "importance"},
            {"template": "What are the real-world applications of {topic}?", "type": "applications"},
            {"template": "Compare {topic} with related concepts.", "type": "compare"}
        ],
        'math': [
            {"template": "Solve: Find the {topic} of the given equation.", "type": "problem"},
            {"template": "Explain the {topic} formula with an example.", "type": "example"},
            {"template": "What is the real-world application of {topic}?", "type": "application"},
            {"template": "Derive the formula for {topic}.", "type": "derivation"}
        ],
        'project': [
            {"template": "What are the key steps to implement {topic}?", "type": "implementation"},
            {"template": "What challenges might you face when building {topic}?", "type": "challenges"},
            {"template": "How would you test a {topic} system?", "type": "testing"},
            {"template": "What technologies would you use for {topic}?", "type": "technology"},
            {"template": "Design a basic architecture for {topic}.", "type": "design"}
        ]
    }
    
    DEFAULT_TEMPLATES = [
        {"template": "What do you know about {topic}?", "type": "general"},
        {"template": "Explain the importance of {topic}.", "type": "importance"},
        {"template": "What are the main aspects of {topic}?", "type": "overview"}
    ]
    
    def __init__(self):
        self.generated_questions = []
    
    def generate_questions(self, subject_name, subject_type='theory', num_questions=3):
        """Generate quiz questions for a subject"""
        subject_name_lower = subject_name.lower()
        topic = self._extract_topic(subject_name_lower)
        
        templates = self.QUESTION_TEMPLATES.get(subject_type, self.DEFAULT_TEMPLATES)
        
        questions = []
        used_templates = []
        
        for i in range(min(num_questions, len(templates))):
            available = [t for t in templates if t['template'] not in used_templates]
            if not available:
                available = templates
            
            template_data = random.choice(available)
            used_templates.append(template_data['template'])
            
            question_text = self._fill_template(template_data['template'], topic, subject_name)
            sample_answer = self._generate_detailed_answer(question_text, topic, subject_type, subject_name)
            
            questions.append({
                'id': f"q_{len(self.generated_questions)}_{i}",
                'question': question_text,
                'type': template_data['type'],
                'sample_answer': sample_answer,
                'difficulty': self._calculate_difficulty(subject_name),
                'topic': topic
            })
        
        self.generated_questions.extend(questions)
        return questions
    
    def _extract_topic(self, subject_name):
        """Extract main topic from subject name"""
        if 'theory of automata' in subject_name or 'automata' in subject_name:
            return "Theory of Automata"
        if 'data structure' in subject_name or 'algorithm' in subject_name or 'dsa' in subject_name:
            return "Data Structures and Algorithms"
        if 'operating system' in subject_name or 'os' in subject_name:
            return "Operating Systems"
        if 'database' in subject_name:
            return "Database Management Systems"
        if 'computer network' in subject_name or 'network' in subject_name:
            return "Computer Networks"
        if 'artificial intelligence' in subject_name or 'ai' in subject_name:
            return "Artificial Intelligence"
        if 'machine learning' in subject_name or 'ml' in subject_name:
            return "Machine Learning"
        
        words = subject_name.split()
        if len(words) > 3:
            return ' '.join(words[:3])
        return subject_name.title()
    
    def _fill_template(self, template, topic, full_name):
        """Fill template placeholders with actual content"""
        question = template.replace('{topic}', topic)
        
        other_topics = ['Arrays', 'Linked Lists', 'Stacks', 'Queues', 'Trees', 'Graphs', 'Recursion']
        other = random.choice([t for t in other_topics if t.lower() != topic.lower()])
        question = question.replace('{topic2}', other)
        question = question.replace('{topic1}', topic)
        
        return question
    
    def _generate_detailed_answer(self, question, topic, subject_type, full_name):
        """Generate detailed sample answer for the question"""
        q_lower = question.lower()
        
        # Theory of Automata specific answers
        if 'theory of automata' in full_name.lower() or 'automata' in full_name.lower():
            if 'define' in q_lower or 'what is' in q_lower:
                return "**Theory of Automata** is the study of abstract machines and automata, and the computational problems that can be solved using them. It includes Finite Automata (DFA/NFA), Pushdown Automata (PDA), and Turing Machines. This forms the foundation of computation theory and helps understand what computers can and cannot compute."
            if 'key concepts' in q_lower or 'importance' in q_lower:
                return "**Key Concepts in Theory of Automata:**\n\n1. **Finite Automata (FA)** - Used in text processing, lexical analysis\n2. **Pushdown Automata (PDA)** - Used in parsing programming languages\n3. **Turing Machines** - Theoretical model of computation\n4. **Regular Expressions** - Pattern matching\n5. **Context-Free Grammars** - Language specification\n\n**Importance:** Automata theory is fundamental to compiler design, artificial intelligence, and understanding computational limits."
            if 'applications' in q_lower:
                return "**Real-world Applications of Theory of Automata:**\n\n• **Compiler Design** - Lexical analysis using Finite Automata\n• **Text Processing** - Pattern matching with regular expressions\n• **Artificial Intelligence** - State machines for AI agents\n• **Network Protocols** - Protocol validation\n• **Digital Circuit Design** - Finite state machines in hardware\n• **Natural Language Processing** - Grammar parsing"
        
        # DSA specific answers
        if 'data structure' in full_name.lower() or 'algorithm' in full_name.lower() or 'dsa' in full_name.lower():
            if 'importance' in q_lower:
                return "**Why Data Structures and Algorithms are Important:**\n\n1. **Efficiency** - Good DSA knowledge helps write faster, memory-efficient code\n2. **Problem Solving** - Provides systematic approaches to complex problems\n3. **Interviews** - Most technical interviews focus heavily on DSA\n4. **Scalability** - Helps design systems that handle large data\n5. **Optimization** - Understanding time/space complexity leads to better solutions"
            if 'key concepts' in q_lower:
                return "**Key Concepts in DSA:**\n\n**Data Structures:** Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables\n\n**Algorithms:** Sorting (Quick, Merge, Bubble), Searching (Binary, Linear), Dynamic Programming, Recursion, BFS, DFS, Dijkstra's Algorithm\n\n**Complexities:** Time complexity (Big O) and Space complexity analysis"
        
        # General answers
        if 'define' in q_lower:
            return f"**{topic}** refers to a fundamental concept in {subject_type} that involves understanding how to organize, process, and analyze information effectively. Mastery of {topic} enables you to solve complex problems efficiently."
        
        if 'importance' in q_lower:
            return f"**{topic}** is crucial because it forms the foundation for understanding more advanced concepts in computer science. Studying {topic} helps develop analytical thinking, improves problem-solving skills, and is essential for technical interviews and real-world software development."
        
        if 'applications' in q_lower:
            return f"**Applications of {topic}:**\n\n• **Software Development** - Used in everyday programming\n• **System Design** - Helps architect scalable solutions\n• **Data Analysis** - Processes large datasets efficiently\n• **Artificial Intelligence** - Powers ML algorithms\n• **Game Development** - Optimizes game logic\n• **Web Development** - Improves backend performance"
        
        # Default answer
        return f"**Sample Answer:**\n\nThis question about {topic} tests your understanding of core concepts. A good answer should include:\n\n1. **Clear definition** - Explain what {topic} means\n2. **Key characteristics** - Describe important features\n3. **Practical examples** - Show real-world usage\n4. **Benefits** - Explain why it matters\n5. **Related concepts** - Connect to other topics\n\n**Example:** In practice, {topic} helps solve problems efficiently by providing structured approaches and optimal solutions."
    
    def _calculate_difficulty(self, subject_name):
        subject_lower = subject_name.lower()
        if any(word in subject_lower for word in ['advanced', 'expert', 'complex']):
            return 'hard'
        if any(word in subject_lower for word in ['intermediate', 'medium']):
            return 'medium'
        return 'easy'
    
    def generate_quiz_for_multiple_subjects(self, subjects, questions_per_subject=2):
        """Generate quiz questions for multiple subjects"""
        all_questions = []
        for subj in subjects:
            questions = self.generate_questions(
                subj.get('name', 'Unknown'),
                subj.get('type', 'theory'),
                questions_per_subject
            )
            all_questions.extend(questions)
        return all_questions