from otree.api import *
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import plotly.graph_objects as go
import io
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit
from django.http import FileResponse, HttpResponse
from reportlab.lib.utils import ImageReader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import ast
import matplotlib.font_manager as fm


doc = """
Your app description
"""
# Import the new function in the imports section
from .utils import plot_attr_comparison, create_scaled_text_image, generate_value_graph

def get_dimensional_hierarchy(player):
    """
    Extracts the participant's similarity ranking and task counts for skills, knowledge, and work activity.

    Parameters:
    - player: oTree Player object containing:
        - 'similarity_order': A comma-separated string ranking different occupational attributes.
        - 's_count_task1', 'k_count_task1', 'wa_count_task1': Counts for different attributes.

    Returns:
    - A tuple of two dictionaries:
        1. similarity_ranking (dict): {'skill': int, 'knowledge': int, 'activity': int}
           * Highest ranked → 30
           * Middle ranked → 20
           * Lowest ranked → 10
        2. counts_dict (dict): {'skill': int, 'knowledge': int, 'activity': int}
           * Extracted participant task counts.
    """

    # ---------- FOR PRODUCTION -------- #
    similarity_list = player.participant.vars['similarity_order'].split(",")
    
    # ------------FOR TESTING-------------- #
    #similarity_list = "Work Environment,Industry/Sector,Tasks,Personal Values,Education and Training,Skills,Knowledge".split(",")
    #print(similarity_list)

    # Extract ranking positions (1-based index)
    rankings = {
        "skill": similarity_list.index("Skills") + 1 if "Skills" in similarity_list else float('inf'),
        "knowledge": similarity_list.index("Knowledge") + 1 if "Knowledge" in similarity_list else float('inf'),
        "activity": similarity_list.index("Tasks") + 1 if "Tasks" in similarity_list else float('inf')  # Work Activity is Tasks
    }

    # Sort attributes by rank (lower index = higher preference)
    sorted_attributes = sorted(rankings, key=rankings.get)

    # Assign scores based on ranking
    similarity_ranking = {
        sorted_attributes[0]: 30,  # Most important (Rank 1) → 30
        sorted_attributes[1]: 20,  # Middle-ranked → 20
        sorted_attributes[2]: 10   # Least important → 10
    }

    # ---------- FOR PRODUCTION -------- #
    counts_dict = {
         "skill": int(player.participant.vars['s_count_task1']),
         "knowledge": int(player.participant.vars['k_count_task1']),
         "activity": int(player.participant.vars['wa_count_task1'])
    }
    
    
    # ------------FOR TESTING-------------- #
    #counts_dict = {
    #    "skill": 12,
    #    "knowledge": 15,
    #    "activity": 18
    #}
    
    sorted_dict = dict(sorted(counts_dict.items(), key=lambda item: item[1], reverse=True))

    return similarity_ranking, sorted_dict

def register_fonts():
    """
    Registers Lato fonts globally so they are available throughout the app.
    This should only run once when the app starts.
    """
    current_app_dir = os.path.dirname(os.path.abspath(__file__))
    # Move one level up to `representations_nova`
    parent_dir = os.path.dirname(current_app_dir)
    font_dir = os.path.join(parent_dir, "fonts")  # Path to the Lato font folder

    # Register Lato font variations
    pdfmetrics.registerFont(TTFont("Lato-Regular", os.path.join(font_dir, "Lato-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Lato-Bold", os.path.join(font_dir, "Lato-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Lato-Italic", os.path.join(font_dir, "Lato-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Lato-Thin", os.path.join(font_dir, "Lato-Thin.ttf")))
    pdfmetrics.registerFont(TTFont("Lato-Light", os.path.join(font_dir, "Lato-Light.ttf")))
    

    print("✅ Lato fonts registered successfully!")
    
    return True

def initialization_var():
    
    k_df = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/k_vec.csv")
    s_df = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/s_vec.csv")
    wa_df = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/wa_vec.csv")
    val_df = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/value_vec.csv")
    
    #print(k_df.columns)
    #print(s_df.columns)
    #print(wa_df.columns) 
    
    #focal_job = 'Actors'
    #print(wa_df[focal_job])
    #print(s_df[focal_job])
    #print(k_df[focal_job])
    
    return k_df, s_df, wa_df, val_df

# Add this to the generate_images_for_pdf function
def generate_images_for_pdf(player, save_path):
    """
    Generate attribute comparison and scaled text images for a participant and save them in their folder.
    """
    
    #-------- FOR PRODUCTION --------------#
    focal_job = player.participant.vars['onet_job']
    target_jobs = [player.participant.vars['attainable_job'], player.participant.vars['dream_job']]
    #print("GENERATE IMAGES")
    #print(target_jobs)
    #print(focal_job)
    
    #-------- FOR TESTING --------------#
    #focal_job = "Floral Designers"
    #target_jobs = ["Actors", "Fashion Designers"]

    attr_list = ['Skill', 'Knowledge', 'Work Activity']
    i = 0
    for target_job in target_jobs:
        for attribute in attr_list:
            if attribute == 'Work Activity':
                #print(wa_df.columns)
                attributes_list = sorted(list(C.wa_data.loc[C.wa_data['Title'] == focal_job, 'Element Name'].unique()))
                focal_vec = ast.literal_eval(list(C.wa_df.loc[C.wa_df['Occupation']==focal_job, 'Importance'])[0])
                target_vec = ast.literal_eval(list(C.wa_df.loc[C.wa_df['Occupation']==target_job, 'Importance'])[0])

            if attribute == 'Knowledge':
                #print(k_df.columns)
                attributes_list = sorted(list(C.k_data.loc[C.k_data['Occupation'] == focal_job, 'knowledge']))
                focal_vec = ast.literal_eval(list(C.k_df.loc[C.k_df['Occupation']==focal_job, 'Importance'])[0])
                target_vec = ast.literal_eval(list(C.k_df.loc[C.k_df['Occupation']==target_job, 'Importance'])[0])

            if attribute == 'Skill':
                #print(k_df.columns)
                attributes_list = sorted(list(C.s_data.loc[C.s_data['Occupation'] == focal_job, 'skill']))
                focal_vec = ast.literal_eval(list(C.s_df.loc[C.s_df['Occupation']==focal_job, 'Importance'])[0])
                target_vec = ast.literal_eval(list(C.s_df.loc[C.s_df['Occupation']==target_job, 'Importance'])[0])               
            
            if i == 1:
                # Save plot in participant folder
                output_path = os.path.join(save_path, f"{attribute}_target_dist.png")
                plot_attr_comparison(focal_vec, target_vec, attributes_list, focal_job, target_job, attribute, output_path)
                
            if i == 0:
                # Save plot in participant folder
                output_path = os.path.join(save_path, f"{attribute}_target_close.png")
                plot_attr_comparison(focal_vec, target_vec, attributes_list, focal_job, target_job, attribute, output_path)
        
        i=i+1
        
    # Generate a scaled text image
    data1, data2 = get_dimensional_hierarchy(player)
    scaled_text_path = os.path.join(save_path, "Scaled_Text.png")
    create_scaled_text_image(data1, data2, dict_name1="Reported", dict_name2="Measured", output_path=scaled_text_path)
    
    # Generate value graph - NEW ADDITION
    #-------- FOR TESTING --------------#
    #values_order_str = "Recognition,Support,Working Conditions,Relationships,Achievement,Independence"
    #onet_job = focal_job  # "Floral Designers"
    #attainable_job = target_jobs[0]  # "Actors"
    #dream_job = target_jobs[1]  # "Fashion Designers"
    
    #-------- FOR PRODUCTION --------------#
    values_order_str = player.participant.vars['values_order']
    onet_job = player.participant.vars['onet_job']
    attainable_job = player.participant.vars['attainable_job']
    dream_job = player.participant.vars['dream_job']
    
    # Path to Lato font
    current_app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_app_dir)
    font_dir = os.path.join(parent_dir, "fonts")
    lato_font_path = os.path.join(font_dir, "Lato-Regular.ttf")
    
    # Save value graph to participant folder
    value_graph_path = os.path.join(save_path, "Value_Graph.png")
    generate_value_graph(
        values_order_str=values_order_str,
        onet_job=onet_job,
        attainable_job=attainable_job,
        dream_job=dream_job,
        val_df=C.val_df,
        output_path=value_graph_path,
        font_path=lato_font_path
    )
def generate_pdf(player, filename, participant_folder):
    """
    Generates a PDF report for a given player based on their survey responses
    and includes explanatory text and visual elements organized in a structured way.
    
    Parameters:
    - player: oTree Player object containing participant data.
    - filename: Path where the final PDF should be saved.
    - participant_folder: Folder where the generated images are stored.
    """
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Lato-Regular", 11)

        page_width, page_height = letter
        left_margin = 50
        max_text_width = page_width - 2 * left_margin
        y_position = 750  # Start position for writing responses

        # **Header**
        c.setFont("Lato-Bold", 13)
        # Center the header
        header_text = "Participant Survey Report"
        header_width = c.stringWidth(header_text, "Lato-Bold", 13)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, header_text)
        y_position -= 30  # Move down slightly
        
        # Add and center "Participant Information" heading
        c.setFont("Lato-Bold", 12)
        info_header = "Participant Information"
        info_width = c.stringWidth(info_header, "Lato-Bold", 12)
        info_x = (page_width - info_width) / 2
        c.drawString(info_x, y_position, info_header)
        y_position -= 20  # Move down for participant details
        
        #-------- FOR PRODUCTION --------------#
        focal_job = player.participant.vars['onet_job']
        dream_job = player.participant.vars['dream_job']
        attainable_job = player.participant.vars['attainable_job']
        
        #-------- FOR TESTING --------------#
        #focal_job = "Floral Designers" 
        #dream_job =  "Actors" 
        #attainable_job =  "Fashion Designers"

        # **Extract and write participant data**
        responses = {
            "Participant Code": player.participant.code,
            "Current/Most Recent Role": player.participant.vars['onet_job'], 
            "Attainable Transition Role": player.participant.vars['attainable_job'], 
            "Dream Transition Role":  player.participant.vars['dream_job'],
            "Education Level": player.educ,
            "Age": player.age,
            "Gender": player.gender,
            "Income": player.income,
            "Ethnicity": player.race
        }

        c.setFont("Lato-Regular", 10.5)

        # Print participant details with no extra spacing
        for key, value in responses.items():
            wrapped_text = simpleSplit(f"{key}: {value}", "Lato-Regular", 10.5, max_text_width)
            for line in wrapped_text:
                c.drawString(left_margin, y_position, line)
                y_position -= 14  # Minimal spacing
                
        # **Add Introduction and Overview Section**
        y_position -= 15  # Add some space before the new section
        c.setFont("Lato-Bold", 12)
        intro_header = "Introduction and Overview"
        intro_width = c.stringWidth(intro_header, "Lato-Bold", 12)
        intro_x = (page_width - intro_width) / 2  # Center the heading
        c.drawString(intro_x, y_position, intro_header)
        y_position -= 20
        
        # Introduction text paragraphs
        c.setFont("Lato-Regular", 10)
        intro_text = [
            "Thank you for participating in our survey on occupations. Career moves can be emotionally and intellectually daunting and we begin with what you know and a clear understanding of where you are in terms of your current capacities and constraints.",
            "Our goal is to help you recognize what defines your mental models of jobs and how these perceptions make some jobs seem more or less attainable, among other factors like personal and institutional constraints. For example, two software engineers may implicitly focus on different attributes based on past education, cultural and personal experiences and hence might consider different options while thinking about career transitions. The more aware we become of our own implicit mental orientations, the better able we will be to direct/channel our career exploration efforts.",
            "We hope to give you insights about your job perceptions, as captured by your survey responses to help you navigate this career transition phase in your professional journey. We start by looking at your judgments of occupational similarity in the comparison tasks, your choices help us understand which attributes of work are prioritized. To analyze and interpret the choices you made throughout the survey and characterize your cognitive profile on occupations, we define job attributes adapted from the O*NET Content Model:",
            "• Skills: Developed capacities that facilitate learning or acquisition of knowledge, performance of tasks that occur across jobs",
            "• Work Activities: Job behaviors and duties performed by workers as a part of job responsibilities",
            "• Knowledge: Organized sets of principles, facts and information that can be applied in helping you to do the job",
            "• Values: Aspects of work that are important to a person's satisfaction"
        ]
        
        # Process the paragraphs
        for paragraph in intro_text:
            wrapped_lines = simpleSplit(paragraph, "Lato-Regular", 10, max_text_width - 10)
            for line in wrapped_lines:
                # Check if we need a new page
                if y_position < 50:
                    c.showPage()
                    y_position = 750
                    c.setFont("Lato-Regular", 10)
                
                c.drawString(left_margin, y_position, line)
                y_position -= 14
            y_position -= 5  # Extra space between paragraphs

        # Helper function to get scaled dimensions
        def get_scaled_dimensions(image_path, max_width, max_height):
            """
            Scales an image proportionally to fit within max_width and max_height.
            """
            img = ImageReader(image_path)
            orig_width, orig_height = img.getSize()  # Original dimensions

            # Calculate scaling factor while maintaining aspect ratio
            scale_factor = min(max_width / orig_width, max_height / orig_height)

            # Compute new dimensions
            new_width = orig_width * scale_factor
            new_height = orig_height * scale_factor

            return new_width, new_height
        
        # Helper function to insert and center an image
        def insert_image(image_path, y_position, max_width=400, max_height=250):
            """
            Inserts an image into the PDF, centering it horizontally on the page.
            """
            if os.path.exists(image_path):
                img = ImageReader(image_path)
                
                # Determine if this is a special image type
                is_special_image = "Scaled_Text.png" in image_path or "Value_Graph.png" in image_path
                
                # Use different dimensions for special images
                if is_special_image:
                    if "Scaled_Text.png" in image_path:
                        # Scaled text needs maximum width for proper centering
                        max_width = page_width - 100  # Use almost full page width (minus margins)
                    else:
                        max_width = 600  # Default for other special images
                    max_height = 450  # Allow more height for special images
                
                # Get scaled dimensions
                orig_width, orig_height = img.getSize()  # Original dimensions
                scale_factor = min(max_width / orig_width, max_height / orig_height)
                new_width = orig_width * scale_factor
                new_height = orig_height * scale_factor

                # Check if the image fits on the current page
                if y_position - new_height < 50:  # Ensure bottom margin space
                    c.showPage()  # Move to a new page
                    y_position = 750  # Reset y position for new page

                # Calculate x position to center the image
                x_position = (page_width - new_width) / 2
                
                # Draw the image
                c.drawImage(img, x_position, y_position - new_height, 
                           width=new_width, height=new_height)
                
                # Return the updated y position
                if is_special_image:
                    return y_position - (new_height + 40)  # More space after special images
                else:
                    return y_position - (new_height + 30)  # Standard spacing
            else:
                print(f"⚠️ Warning: Image not found - {image_path}")
                return y_position

        # **Retrieve images from participant's folder**
        target_dist_images = [
            os.path.join(participant_folder, "Skill_target_dist.png"),
            os.path.join(participant_folder, "Knowledge_target_dist.png"),
            os.path.join(participant_folder, "Work Activity_target_dist.png"),
        ]

        target_close_images = [
            os.path.join(participant_folder, "Skill_target_close.png"),
            os.path.join(participant_folder, "Knowledge_target_close.png"),
            os.path.join(participant_folder, "Work Activity_target_close.png"),
        ]

        scaled_text_image = os.path.join(participant_folder, "Scaled_Text.png")
        values_image = os.path.join(participant_folder, "Value_Graph.png")

        # REORDERED SECTIONS - Start with Occupational Representations
        # Start a new page for Dimensional Hierarchies (Occupational Representations)
        c.showPage()
        y_position = 750
        
        # Add the "Dimensional Hierarchies" section header and description
        c.setFont("Lato-Bold", 12)
        dim_header = "Occupational Representations"
        header_width = c.stringWidth(dim_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, dim_header)
        y_position -= 25
        
        # Add the new introduction paragraph for Dimensional Hierarchies
        c.setFont("Lato-Regular", 10)
        intro_text = "This graph shows how you make sense of which jobs are similar. It has two sides. On the left side (Reported), you'll see how you said different parts of a job—like skills or tasks—matter to you when comparing jobs. On the right side (Measured), you'll see what your choices during the task suggest mattered most. This reveals what was important to you based on how you chose, not just what you said."
        
        wrapped_intro = simpleSplit(intro_text, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_intro:
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        
        y_position -= 10  # Extra space after the introduction
        
        # Add the explanation bullet points
        c.setFont("Lato-Regular", 10)
        dim_text = [
            "In this graph, the dimensions are listed from top to bottom, with the most important ones at the top. The left side shows how you ranked what matters most when thinking about how jobs are similar. The right side shows what seemed most important based on the choices you made during the task. The size of the words also tells you how important each dimension is—bigger words mean more important. You can look at both sides to see if they match or if your choices tell a different story than what you first said.."
        ]
        
        for line in dim_text:
            wrapped_lines = simpleSplit(line, "Lato-Regular", 10, max_text_width - 10)
            for wrapped in wrapped_lines:
                # Check if we need a new page
                if y_position < 50:
                    c.showPage()
                    y_position = 750
                    c.setFont("Lato-Regular", 10)
                
                c.drawString(left_margin, y_position, wrapped)
                y_position -= 14
            y_position -= 2  # Small extra space between bullet points
        
        y_position -= 15  # Extra space
        
        # Add the paragraph about differences
        diff_text = "Looking at both sides of the graph can help you learn something important. Sometimes, what we think matters to us is different from what actually affects our choices. This can show hidden priorities you didn't know you had. Understanding both what you said was important and what your choices show can give you a fuller picture of how you see jobs—and might even help you discover new kinds of jobs that fit you well. Knowing how you judge job similarity matters because it can shape the way you think about career options and which paths feel right for you."
        
        wrapped_diff = simpleSplit(diff_text, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_diff:
            # Check if we need a new page
            if y_position < 50:
                c.showPage()
                y_position = 750
                c.setFont("Lato-Regular", 10)
            
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        
        y_position -= 15  # Extra space before new orientation text
        
        # ADD NEW TEXT ABOUT DIFFERENT ORIENTATIONS
        c.setFont("Lato-Bold", 11)
        orientation_header = "What do different orientations mean?"
        c.drawString(left_margin, y_position, orientation_header)
        y_position -= 18
        
        c.setFont("Lato-Regular", 10)
        orientation_intro = "People think about jobs in different ways. Some focus on what a person needs to be able to do, others focus on what a person actually does day-to-day, and still others think about what a person needs to know. These differences shape how we judge whether two jobs are similar or different."
        
        # Italicize parts of the text
        orientation_intro_parts = [
            {"text": "People think about jobs in different ways. Some focus on ", "style": "Regular"},
            {"text": "what a person needs to be able to do", "style": "Italic"},
            {"text": ", others focus on ", "style": "Regular"},
            {"text": "what a person actually does day-to-day", "style": "Italic"},
            {"text": ", and still others think about ", "style": "Regular"},
            {"text": "what a person needs to know", "style": "Italic"},
            {"text": ". These differences shape how we judge whether two jobs are similar or different.", "style": "Regular"}
        ]
        
        # Build and wrap the orientation intro with styled parts
        x_pos = left_margin
        wrapped_text = simpleSplit(orientation_intro, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_text:
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        
        y_position -= 5  # Extra space after intro paragraph
        
        # Add bullet points for each orientation
        # Instead of trying to style specific words in bullets, we'll draw each bullet completely
        # Skills-oriented perspective
        c.setFont("Lato-Regular", 10)
        skills_bullet = "• A skills-oriented perspective means you tend to compare jobs based on the kinds of abilities or competencies they require—things like problem-solving, communication, or manual dexterity. If you're skills-oriented, you might see two jobs as similar because they both demand, say, critical thinking—even if they're in different industries."
        wrapped_skills = simpleSplit(skills_bullet, "Lato-Regular", 10, max_text_width - 10)
        for i, line in enumerate(wrapped_skills):
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        y_position -= 5  # Extra space
        
        # Activities-oriented perspective
        activities_bullet = "• An activities-oriented perspective means you focus on the "
        c.drawString(left_margin, y_position, activities_bullet)
        
        # Measure the width of the first part
        first_width = c.stringWidth(activities_bullet, "Lato-Regular", 10)
        
        # Add the italic part
        c.setFont("Lato-Italic", 10)
        italic_text = "daily tasks and responsibilities"
        c.drawString(left_margin + first_width, y_position, italic_text)
        
        # Measure the width of the italic part
        italic_width = c.stringWidth(italic_text, "Lato-Italic", 10)
        
        # Add the rest of the line
        c.setFont("Lato-Regular", 10)
        rest_text = " of the job. You might think two roles are similar because both involve managing people, repairing equipment, or working with customers rather than what skills or knowledge they require."
        
        # Check if the remaining text fits on the current line
        if first_width + italic_width + c.stringWidth(rest_text, "Lato-Regular", 10) > max_text_width - 10:
            # Move to next line and indent
            y_position -= 14
            wrapped_rest = simpleSplit(rest_text, "Lato-Regular", 10, max_text_width - 20)  # Extra indent
            for i, line in enumerate(wrapped_rest):
                c.drawString(left_margin + 10, y_position, line)  # Indent for continuation
                y_position -= 14
        else:
            # Fits on the same line
            c.drawString(left_margin + first_width + italic_width, y_position, rest_text)
            y_position -= 14
        
        y_position -= 5  # Extra space
        
        # Knowledge-oriented perspective
        knowledge_bullet = "• A knowledge-oriented perspective means you tend to organize jobs based on the subject matter or domains of expertise they involve—like law, engineering, healthcare, or design. You might view jobs as related if they draw on similar kinds of knowledge, even if they involve very different kinds of work."
        wrapped_knowledge = simpleSplit(knowledge_bullet, "Lato-Regular", 10, max_text_width - 10)
        for i, line in enumerate(wrapped_knowledge):
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        
        y_position -= 5  # Extra space between bullets
        
        # Add the "Why this matters" conclusion
        c.setFont("Lato-Bold", 10)
        c.drawString(left_margin, y_position, "Why this matters:")
        y_position -= 14
        
        c.setFont("Lato-Regular", 10)
        why_text = "Understanding your orientation can shed light on why certain jobs feel like good options to you—even if others might not make the same connection. It can also reveal opportunities you might not have considered, simply because they don't align with how you typically organize the occupational world."
        
        # Process with italic styling for "why"
        wrapped_why = simpleSplit(why_text, "Lato-Regular", 10, max_text_width - 10)
        for i, line in enumerate(wrapped_why):
            # Replace "why" with italic "why" if it's in this line
            if "why" in line and i == 0:  # Only in the first line
                parts = line.split("why", 1)
                c.drawString(left_margin, y_position, parts[0])
                
                c.setFont("Lato-Italic", 10)
                c.drawString(left_margin + c.stringWidth(parts[0], "Lato-Regular", 10), 
                           y_position, "why")
                
                c.setFont("Lato-Regular", 10)
                remaining = parts[1]
                c.drawString(left_margin + c.stringWidth(parts[0], "Lato-Regular", 10) + 
                           c.stringWidth("why", "Lato-Italic", 10), y_position, remaining)
            else:
                c.drawString(left_margin, y_position, line)
            
            y_position -= 14
        
        y_position -= 15  # Extra space before the image
        
        # Insert the Scaled Text image
        if os.path.exists(scaled_text_image):
            # Use the insert_image function with max_width set to use almost the full page width
            y_position = insert_image(scaled_text_image, y_position)
        
        # Values Alignment Section (2nd section)
        c.showPage()  # Start a new page
        y_position = 750
        
        # Add the "Values Alignment" section header
        c.setFont("Lato-Bold", 12)
        values_header = "Your Values Alignment with Different Job Roles"
        header_width = c.stringWidth(values_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, values_header)
        y_position -= 25
        
        # Add the explanation text for Values section
        c.setFont("Lato-Regular", 10)
        values_text = [
            "This graph shows your values and how they match with different jobs—your current or most recent job, a job that fits well with your current skills and experience, and your dream job. The values that are higher on the graph are more important to you, based on how you ranked the values in the survey. Each circle stands for a value, and the size of the circle shows how much that value is expressed or put into action in each job. Big circles mean the value is something that gets used or matters a lot in that job, while small circles mean it plays a smaller role. You can use this graph to see which jobs match the values that matter most to you."
        ]
        
        for line in values_text:
            wrapped_lines = simpleSplit(line, "Lato-Regular", 10, max_text_width - 10)
            for wrapped in wrapped_lines:
                c.drawString(left_margin, y_position, wrapped)
                y_position -= 14
            y_position -= 2  # Small extra space between bullet points
        
        y_position -= 20  # Extra space before the image
        
        # Insert the Values Graph image
        if os.path.exists(values_image):
            y_position = insert_image(values_image, y_position, 500, 300)
        
        # Gap-Overlap Section (3rd section)
        c.showPage()  # Start a new page
        y_position = 750
        
        # Add the "Gap-Overlap" section header and description
        c.setFont("Lato-Bold", 12)
        gap_header = "Gap-Overlap in Skills, Knowledge, Work Activities"
        header_width = c.stringWidth(gap_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, gap_header)
        y_position -= 25
        
        # Add the description text for Gap-Overlap section
        c.setFont("Lato-Regular", 10)
        gap_text = [
            "Each graph compares your current (or most recent) job with a job you'd like to have. It shows how the two jobs differ in terms of skills, knowledge, or tasks. The bars point left or right to show the difference. Bars pointing left mean you might need to learn more in that area, while bars pointing right mean you're already strong in that area. If there's no bar, it means you're right on par—you and the job match in that area. The different skills, knowledge, or tasks are arranged from top to bottom based on how important they are for the job you want, with the most important ones at the top."
        ]
        
        for line in gap_text:
            wrapped_lines = simpleSplit(line, "Lato-Regular", 10, max_text_width - 10)
            for wrapped in wrapped_lines:
                c.drawString(left_margin, y_position, wrapped)
                y_position -= 14
            y_position -= 2  # Small extra space between bullet points
        
        y_position -= 10  # Extra space after the description
        
        # **Display alignment graphs**
        all_alignment_images = target_close_images + target_dist_images
        graph_count = 0
        
        for img_path in all_alignment_images:
            if os.path.exists(img_path):
                # Every two graphs per page
                if graph_count % 2 == 0 and graph_count > 0:
                    c.showPage()  # Start a new page
                    y_position = 750  # Reset y position

                # Center the graph title
                if "Skill_target_close.png" in img_path:
                    title_text = f"Skill: {focal_job} to {attainable_job}"
                elif "Skill_target_dist.png" in img_path:
                    title_text = f"Skill: {focal_job} to {dream_job}"
                
                if "Knowledge_target_close.png" in img_path:
                    title_text = f"Knowledge: {focal_job} to {attainable_job}"
                elif "Knowledge_target_dist.png" in img_path:
                    title_text = f"Knowledge: {focal_job} to {dream_job}"
                    
                if "Work Activity_target_close.png" in img_path:
                    title_text = f"Work Activity: {focal_job} to {attainable_job}"
                elif "Work Activity_target_dist.png" in img_path:
                    title_text = f"Work Activity: {focal_job} to {dream_job}"
                
                c.setFont("Lato-Bold", 10)
                title_width = c.stringWidth(title_text, "Lato-Bold", 10)
                title_x = (page_width - title_width) / 2
                c.drawString(title_x, y_position, title_text)
                
                y_position -= 30
                y_position = insert_image(img_path, y_position)
                
                graph_count += 1
        
        # Conclusion Section (4th section)
        c.showPage()  # Start a new page
        y_position = 750
        
        # Add the "Conclusion" section header
        c.setFont("Lato-Bold", 12)
        conclusion_header = "Conclusion"
        header_width = c.stringWidth(conclusion_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, conclusion_header)
        y_position -= 25
        
        # Add the conclusion text
        c.setFont("Lato-Regular", 10)
        conclusion_text = "We hope this report offers valuable insights into your career exploration and decision-making processes. Career development involves continuously reflecting on your skills, values, and interests to make informed and fulfilling career choices. The occupations analyzed in this report, drawn from the O*NET database, represent broad occupational categories and highlight general patterns and alignments with your current profile. These insights serve as a foundation for identifying career paths and opportunities that resonate with your skills, knowledge, and values. However, specific roles within these broad categories may vary considerably. Considering detailed aspects of these occupations can further align your career choices with your unique aspirations and experiences."
        
        wrapped_conclusion = simpleSplit(conclusion_text, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_conclusion:
            c.drawString(left_margin, y_position, line)
            y_position -= 14

        # **Save the PDF**
        c.save()
        print(f"✅ PDF successfully saved: {filename}")

        return filename  # Return the filename for later use

    except Exception as e:
        print(f"❌ ERROR saving PDF: {e}")
        import traceback
        traceback.print_exc()  # Print the full traceback for debugging

def generate_pdf2(player, filename, participant_folder):
    """
    Generates a PDF report for a given player based on their survey responses
    and includes explanatory text and visual elements organized in a structured way.
    
    Parameters:
    - player: oTree Player object containing participant data.
    - filename: Path where the final PDF should be saved.
    - participant_folder: Folder where the generated images are stored.
    """
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Lato-Regular", 11)

        page_width, page_height = letter
        left_margin = 50
        max_text_width = page_width - 2 * left_margin
        y_position = 750  # Start position for writing responses

        # **Header**
        c.setFont("Lato-Bold", 13)
        # Center the header
        header_text = "Participant Survey Report"
        header_width = c.stringWidth(header_text, "Lato-Bold", 13)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, header_text)
        y_position -= 30  # Move down slightly
        
        # Add and center "Participant Information" heading
        c.setFont("Lato-Bold", 12)
        info_header = "Participant Information"
        info_width = c.stringWidth(info_header, "Lato-Bold", 12)
        info_x = (page_width - info_width) / 2
        c.drawString(info_x, y_position, info_header)
        y_position -= 20  # Move down for participant details
        
        #-------- FOR PRODUCTION --------------#
        focal_job = player.participant.vars['onet_job']
        dream_job = player.participant.vars['dream_job']
        attainable_job = player.participant.vars['attainable_job']
        
        #-------- FOR TESTING --------------#
        #focal_job = "Floral Designers" 
        #dream_job =  "Actors" 
        #attainable_job =  "Fashion Designers"

        # **Extract and write participant data**
        responses = {
            "Participant Code": player.participant.code,
            "Current/Most Recent Role": player.participant.vars['onet_job'], 
            "Attainable Transition Role": player.participant.vars['attainable_job'], 
            "Dream Transition Role":  player.participant.vars['dream_job'],
            "Education Level": player.educ,
            "Age": player.age,
            "Gender": player.gender,
            "Income": player.income,
            "Ethnicity": player.race
        }

        c.setFont("Lato-Regular", 10.5)

        # Print participant details with no extra spacing
        for key, value in responses.items():
            wrapped_text = simpleSplit(f"{key}: {value}", "Lato-Regular", 10.5, max_text_width)
            for line in wrapped_text:
                c.drawString(left_margin, y_position, line)
                y_position -= 14  # Minimal spacing
                
        # **Add Introduction and Overview Section**
        y_position -= 15  # Add some space before the new section
        c.setFont("Lato-Bold", 12)
        intro_header = "Introduction and Overview"
        intro_width = c.stringWidth(intro_header, "Lato-Bold", 12)
        intro_x = (page_width - intro_width) / 2  # Center the heading
        c.drawString(intro_x, y_position, intro_header)
        y_position -= 20
        
        # Introduction text paragraphs
        c.setFont("Lato-Regular", 10)
        intro_text = [
            "Thank you for participating in our survey on occupations. Career moves can be emotionally and intellectually daunting and we begin with what you know and a clear understanding of where you are in terms of your current capacities and constraints.",
            "Our goal is to help you recognize what defines your mental models of jobs and how these perceptions make some jobs seem more or less attainable, among other factors like personal and institutional constraints. For example, two software engineers may implicitly focus on different attributes based on past education, cultural and personal experiences and hence might consider different options while thinking about career transitions. The more aware we become of our own implicit mental orientations, the better able we will be to direct/channel our career exploration efforts.",
            "We hope to give you insights about your job perceptions, as captured by your survey responses to help you navigate this career transition phase in your professional journey. We start by looking at your judgments of occupational similarity in the comparison tasks, your choices help us understand which attributes of work are prioritized. To analyze and interpret the choices you made throughout the survey and characterize your cognitive profile on occupations, we define job attributes adapted from the O*NET Content Model:",
            "• Skills: Developed capacities that facilitate learning or acquisition of knowledge, performance of tasks that occur across jobs",
            "• Work Activities: Job behaviors and duties performed by workers as a part of job responsibilities",
            "• Knowledge: Organized sets of principles, facts and information that can be applied in helping you to do the job",
            "• Values: Aspects of work that are important to a person's satisfaction"
        ]
        
        # Process the paragraphs
        for paragraph in intro_text:
            wrapped_lines = simpleSplit(paragraph, "Lato-Regular", 10, max_text_width - 10)
            for line in wrapped_lines:
                # Check if we need a new page
                if y_position < 50:
                    c.showPage()
                    y_position = 750
                    c.setFont("Lato-Regular", 10)
                
                c.drawString(left_margin, y_position, line)
                y_position -= 14
            y_position -= 5  # Extra space between paragraphs

        # Helper function to get scaled dimensions
        def get_scaled_dimensions(image_path, max_width, max_height):
            """
            Scales an image proportionally to fit within max_width and max_height.
            """
            img = ImageReader(image_path)
            orig_width, orig_height = img.getSize()  # Original dimensions

            # Calculate scaling factor while maintaining aspect ratio
            scale_factor = min(max_width / orig_width, max_height / orig_height)

            # Compute new dimensions
            new_width = orig_width * scale_factor
            new_height = orig_height * scale_factor

            return new_width, new_height
        
        # Helper function to insert and center an image
        def insert_image(image_path, y_position, max_width=400, max_height=250):
            """
            Inserts an image into the PDF, centering it horizontally on the page.
            """
            if os.path.exists(image_path):
                img = ImageReader(image_path)
                
                # Determine if this is a special image type
                is_special_image = "Scaled_Text.png" in image_path or "Value_Graph.png" in image_path
                
                # Use different dimensions for special images
                if is_special_image:
                    if "Scaled_Text.png" in image_path:
                        # Scaled text needs maximum width for proper centering
                        max_width = page_width - 100  # Use almost full page width (minus margins)
                    else:
                        max_width = 600  # Default for other special images
                    max_height = 450  # Allow more height for special images
                
                # Get scaled dimensions
                orig_width, orig_height = img.getSize()  # Original dimensions
                scale_factor = min(max_width / orig_width, max_height / orig_height)
                new_width = orig_width * scale_factor
                new_height = orig_height * scale_factor

                # Check if the image fits on the current page
                if y_position - new_height < 50:  # Ensure bottom margin space
                    c.showPage()  # Move to a new page
                    y_position = 750  # Reset y position for new page

                # Calculate x position to center the image
                x_position = (page_width - new_width) / 2
                
                # Draw the image
                c.drawImage(img, x_position, y_position - new_height, 
                           width=new_width, height=new_height)
                
                # Return the updated y position
                if is_special_image:
                    return y_position - (new_height + 40)  # More space after special images
                else:
                    return y_position - (new_height + 30)  # Standard spacing
            else:
                print(f"⚠️ Warning: Image not found - {image_path}")
                return y_position

        # **Retrieve images from participant's folder**
        target_dist_images = [
            os.path.join(participant_folder, "Skill_target_dist.png"),
            os.path.join(participant_folder, "Knowledge_target_dist.png"),
            os.path.join(participant_folder, "Work Activity_target_dist.png"),
        ]

        target_close_images = [
            os.path.join(participant_folder, "Skill_target_close.png"),
            os.path.join(participant_folder, "Knowledge_target_close.png"),
            os.path.join(participant_folder, "Work Activity_target_close.png"),
        ]

        scaled_text_image = os.path.join(participant_folder, "Scaled_Text.png")
        values_image = os.path.join(participant_folder, "Value_Graph.png")

        # Start a new page for the alignment graphs
        c.showPage()
        y_position = 750
        
        # Add the "Gap-Overlap" section header and description
        c.setFont("Lato-Bold", 12)
        gap_header = "Gap-Overlap in Skills, Knowledge, Work Activities"
        header_width = c.stringWidth(gap_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, gap_header)
        y_position -= 25
        
        # Add the description text for Gap-Overlap section
        c.setFont("Lato-Regular", 10)
        gap_text = [
            "Each graph compares your current (or most recent) job with a job you'd like to have. It shows how the two jobs differ in terms of skills, knowledge, or tasks. The bars point left or right to show the difference. Bars pointing left mean you might need to learn more in that area, while bars pointing right mean you're already strong in that area. If there's no bar, it means you're right on par—you and the job match in that area. The different skills, knowledge, or tasks are arranged from top to bottom based on how important they are for the job you want, with the most important ones at the top."
        ]
        
        for line in gap_text:
            wrapped_lines = simpleSplit(line, "Lato-Regular", 10, max_text_width - 10)
            for wrapped in wrapped_lines:
                c.drawString(left_margin, y_position, wrapped)
                y_position -= 14
            y_position -= 2  # Small extra space between bullet points
        
        y_position -= 10  # Extra space after the description
        
        # **Display alignment graphs**
        all_alignment_images = target_close_images + target_dist_images
        graph_count = 0
        
        for img_path in all_alignment_images:
            if os.path.exists(img_path):
                # Every two graphs per page
                if graph_count % 2 == 0 and graph_count > 0:
                    c.showPage()  # Start a new page
                    y_position = 750  # Reset y position

                # Center the graph title
                if "Skill_target_close.png" in img_path:
                    title_text = f"Skill: {focal_job} to {attainable_job}"
                elif "Skill_target_dist.png" in img_path:
                    title_text = f"Skill: {focal_job} to {dream_job}"
                
                if "Knowledge_target_close.png" in img_path:
                    title_text = f"Knowledge: {focal_job} to {attainable_job}"
                elif "Knowledge_target_dist.png" in img_path:
                    title_text = f"Knowledge: {focal_job} to {dream_job}"
                    
                if "Work Activity_target_close.png" in img_path:
                    title_text = f"Work Activity: {focal_job} to {attainable_job}"
                elif "Work Activity_target_dist.png" in img_path:
                    title_text = f"Work Activity: {focal_job} to {dream_job}"
                
                c.setFont("Lato-Bold", 10)
                title_width = c.stringWidth(title_text, "Lato-Bold", 10)
                title_x = (page_width - title_width) / 2
                c.drawString(title_x, y_position, title_text)
                
                y_position -= 30
                y_position = insert_image(img_path, y_position)
                
                graph_count += 1
        
        # Start a new page for the Dimensional Hierarchies section
        c.showPage()
        y_position = 750
        
        # Add the "Dimensional Hierarchies" section header and description
        c.setFont("Lato-Bold", 12)
        dim_header = "Occupational Representations"
        header_width = c.stringWidth(dim_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, dim_header)
        y_position -= 25
        
        # Add the new introduction paragraph for Dimensional Hierarchies
        c.setFont("Lato-Regular", 10)
        intro_text = "This graph shows how you make sense of which jobs are similar. It has two sides. On the left side (Reported), you'll see how you said different parts of a job—like skills or tasks—matter to you when comparing jobs. On the right side (Measured), you'll see what your choices during the task suggest mattered most. This reveals what was important to you based on how you chose, not just what you said."
        
        wrapped_intro = simpleSplit(intro_text, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_intro:
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        
        y_position -= 10  # Extra space after the introduction
        
        # Add the explanation bullet points
        c.setFont("Lato-Regular", 10)
        dim_text = [
            "In this graph, the dimensions are listed from top to bottom, with the most important ones at the top. The left side shows how you ranked what matters most when thinking about how jobs are similar. The right side shows what seemed most important based on the choices you made during the task. The size of the words also tells you how important each dimension is—bigger words mean more important. You can look at both sides to see if they match or if your choices tell a different story than what you first said.."
        ]
        
        for line in dim_text:
            wrapped_lines = simpleSplit(line, "Lato-Regular", 10, max_text_width - 10)
            for wrapped in wrapped_lines:
                # Check if we need a new page
                if y_position < 50:
                    c.showPage()
                    y_position = 750
                    c.setFont("Lato-Regular", 10)
                
                c.drawString(left_margin, y_position, wrapped)
                y_position -= 14
            y_position -= 2  # Small extra space between bullet points
        
        y_position -= 15  # Extra space
        
        # Add the paragraph about differences
        diff_text = "Looking at both sides of the graph can help you learn something important. Sometimes, what we think matters to us is different from what actually affects our choices. This can show hidden priorities you didn't know you had. Understanding both what you said was important and what your choices show can give you a fuller picture of how you see jobs—and might even help you discover new kinds of jobs that fit you well. Knowing how you judge job similarity matters because it can shape the way you think about career options and which paths feel right for you."
        
        wrapped_diff = simpleSplit(diff_text, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_diff:
            # Check if we need a new page
            if y_position < 50:
                c.showPage()
                y_position = 750
                c.setFont("Lato-Regular", 10)
            
            c.drawString(left_margin, y_position, line)
            y_position -= 14
        
        y_position -= 15  # Extra space before the image
        
        # Insert the Scaled Text image - CENTER IT PROPERLY
        if os.path.exists(scaled_text_image):
            # Use the insert_image function with max_width set to use almost the full page width
            y_position = insert_image(scaled_text_image, y_position)
        
        # Values + Conclusion on the same page
        c.showPage()
        y_position = 750
        
        # Add the "Values Alignment" section header
        c.setFont("Lato-Bold", 12)
        values_header = "Your Values Alignment with Different Job Roles"
        header_width = c.stringWidth(values_header, "Lato-Bold", 12)
        header_x = (page_width - header_width) / 2
        c.drawString(header_x, y_position, values_header)
        y_position -= 25
        
        # Add the explanation text for Values section
        c.setFont("Lato-Regular", 10)
        values_text = [
            "This graph shows your values and how they match with different jobs—your current or most recent job, a job that fits well with your current skills and experience, and your dream job. The values that are higher on the graph are more important to you, based on how you ranked the values in the survey. Each circle stands for a value, and the size of the circle shows how much that value is expressed or put into action in each job. Big circles mean the value is something that gets used or matters a lot in that job, while small circles mean it plays a smaller role. You can use this graph to see which jobs match the values that matter most to you."
        ]
        
        for line in values_text:
            wrapped_lines = simpleSplit(line, "Lato-Regular", 10, max_text_width - 10)
            for wrapped in wrapped_lines:
                c.drawString(left_margin, y_position, wrapped)
                y_position -= 14
            y_position -= 2  # Small extra space between bullet points
        
        y_position -= 20  # Extra space before the image
        
        # Insert the Values Graph image
        if os.path.exists(values_image):
            # Save the y position before drawing the image
            pre_image_y = y_position
            y_position = insert_image(values_image, y_position, 500, 300)  # Reduced height to leave room for conclusion
            
            # Check if there's enough space for the conclusion (at least 150 points)
            # If not enough space, start a new page
            if y_position < 150:  # Need at least 150 points for conclusion
                c.showPage()
                y_position = 750
                # Add the "Conclusion" section header on new page
                c.setFont("Lato-Bold", 12)
                conclusion_header = "Conclusion"
                header_width = c.stringWidth(conclusion_header, "Lato-Bold", 12)
                header_x = (page_width - header_width) / 2
                c.drawString(header_x, y_position, conclusion_header)
                y_position -= 25
            else:
                # Add the "Conclusion" section header on same page
                y_position -= 20  # Extra space before conclusion
                c.setFont("Lato-Bold", 12)
                conclusion_header = "Conclusion"
                header_width = c.stringWidth(conclusion_header, "Lato-Bold", 12)
                header_x = (page_width - header_width) / 2
                c.drawString(header_x, y_position, conclusion_header)
                y_position -= 25
            
        # Add the conclusion text
        c.setFont("Lato-Regular", 10)
        conclusion_text = "We hope this report offers valuable insights into your career exploration and decision-making processes. Career development involves continuously reflecting on your skills, values, and interests to make informed and fulfilling career choices. The occupations analyzed in this report, drawn from the O*NET database, represent broad occupational categories and highlight general patterns and alignments with your current profile. These insights serve as a foundation for identifying career paths and opportunities that resonate with your skills, knowledge, and values. However, specific roles within these broad categories may vary considerably. Considering detailed aspects of these occupations can further align your career choices with your unique aspirations and experiences."
        
        wrapped_conclusion = simpleSplit(conclusion_text, "Lato-Regular", 10, max_text_width - 10)
        for line in wrapped_conclusion:
            c.drawString(left_margin, y_position, line)
            y_position -= 14

        # **Save the PDF**
        c.save()
        print(f"✅ PDF successfully saved: {filename}")

        return filename  # Return the filename for later use

    except Exception as e:
        print(f"❌ ERROR saving PDF: {e}")
        import traceback
        traceback.print_exc()  # Print the full traceback for debugging

class C(BaseConstants):
    NAME_IN_URL = 'representations_q_1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    font_run = register_fonts()
    k_data = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/knowledge.csv", index_col=0)
    s_data = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/skills.csv", index_col=0)
    wa_data = pd.read_excel(os.path.dirname(os.path.abspath(__file__))+"/Work Activities.xlsx")
    val_data = pd.read_csv(os.path.dirname(os.path.abspath(__file__))+"/values.csv", index_col=0)
    k_df, s_df, wa_df, val_df = initialization_var()

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    
    educ = models.StringField(choices=['Less than high school diploma', 'High school graduate or equivalent (eg: GED)', 
                                       'Some college credit, no degree', 'Trade/Technical/Vocational School', 
                                       "Bachelor's degree", "Master's degree", 'Doctorate degree', 'Other'],
        label='What is the highest level of school you have completed or the highest degree you have received?',
        widget=widgets.RadioSelect,)
    
    educ_other = models.StringField(blank = True)
    
    age = models.IntegerField(label='What is your age?', min=17, max=125)
    
    gender = models.StringField(
        choices=['Male', "Female", "Other"],
        label='How would you describe your gender?',
        widget=widgets.RadioSelect,
    )
    
    gender_other = models.StringField(blank = True)
    
    income = models.StringField(choices=['$0-$30,000','$31,000-$60,000',
                                         '$61,000-$90,000', '$91,000-$120,000',
                                         '$120,000+'],
        label='What is the total annual income from your current or most recent role?',
        widget=widgets.RadioSelect,)
    
    race = models.StringField(choices=['American Indian or Alaska Native','Asian or Asian American',
                                       'Black or African American','Latino or Latina / Hispanic or Latinx','White or Caucasian',
                                       'Middle Eastern','Native Hawaiian or other Pacific Islander','Other'],
        label='Which of the following best describe(s) you?',
        widget=widgets.RadioSelect,)
    
    race_other = models.StringField(blank = True)
    race_all = models.StringField(blank = True)
    
    comments = models.StringField(label = 'Do you have any questions or feedback for the researchers?')


# PAGES
class Instructions(Page):
    pass

class Instructions0(Page):
    pass

class Questions1(Page):
    
    form_model = 'player'
    #form_fields = ['educ', 'educ_other', 'age', 'gender', 'gender_other', 'income',
    #              'race', 'race_other','comments']
    
    form_fields = ['educ', 'educ_other','age', 'gender', 'race', 'income',
                  'comments', 'gender', 'gender_other', 'race_all', 'race_other']
    
    # def error_message(player, values):
    #     if values["educ"] == "Other - please specify" and not values["other_educ"].strip():
    #         return "Please specify your choice in the 'Other' field."
    
    # def error_message(self, values):
    #     if values['educ'] == 'Other' and not values['educ_other'].strip():
    #         return 'Please specify your choice for education.'
    
class Questions1_v2(Page):
    
    form_model = 'player'
    #form_fields = ['educ', 'educ_other', 'age', 'gender', 'gender_other', 'income',
    #              'race', 'race_other','comments']
    
    form_fields = ['educ', 'educ_other','age', 'race', 'income',
                  'comments', 'gender', 'gender_other', 'race_all', 'race_other']
    
class GeneratePDFPage(Page):
    """
    This page displays a message and generates a PDF in the background.
    The "Next" button is disabled until processing is complete.
    """

    @staticmethod
    def vars_for_template(player):
        """
        Generate the PDF and create a unique folder for storing images and the final report.
        """
        import time

        # Get the absolute path of the current app directory
        current_app_dir = os.path.dirname(os.path.abspath(__file__))  # Points to representations_q
        # Move one level up to `representations_nova`
        parent_dir = os.path.dirname(current_app_dir)

        # Define the main reports directory inside `_static/reports`
        reports_directory = os.path.join(parent_dir, "_static/reports")

        # Ensure the main reports directory exists
        if not os.path.exists(reports_directory):
            os.makedirs(reports_directory)  # Create the folder if it doesn't exist

        # Fetch session code, participant code, and participant ID
        session_code = player.session.code  # Unique session identifier
        participant_code = player.participant.code  # Unique participant identifier
        participant_id = player.id_in_group  # Numeric ID within the group

        # Construct a unique folder name based on the PDF filename
        folder_name = f"{session_code}_{participant_code}_{participant_id}"
        participant_folder = os.path.join(reports_directory, folder_name)

        # Ensure the participant-specific folder exists
        if not os.path.exists(participant_folder):
            os.makedirs(participant_folder)  # Create the folder

        # Define the path for the final PDF file inside the participant folder
        pdf_filename = os.path.join(participant_folder, f"{folder_name}.pdf")

        print("Creating participant folder:", participant_folder)
        print("Going to generate PDF:", pdf_filename)

        # Generate images and save them in the participant folder
        generate_images_for_pdf(player, participant_folder)  # Function to generate images

        # Generate the PDF using the stored images
        generate_pdf(player, pdf_filename, participant_folder)

        # Simulate processing delay (Optional: remove in production)
        time.sleep(3)  # Simulate a delay of 3 seconds

        return {"message": "Processing complete! Click Next to continue."}

    @staticmethod
    def js_vars(player):
        """
        Pass a flag to JavaScript so it can disable the Next button while processing.
        """
        return {"processing_done": False}  # Initially False

class DownloadReport(Page):
    def vars_for_template(player):
        """
        Generates the file path to the participant's PDF report and makes it available for download.
        The report is stored inside a participant-specific folder within `_static/reports/`.
        """
        # Get the absolute path of the current app directory
        current_app_dir = os.path.dirname(os.path.abspath(__file__))  # Points to representations_q
        parent_dir = os.path.dirname(current_app_dir)  # Move up to representations_nova

        # Define the main reports directory
        reports_directory = os.path.join(parent_dir, "_static/reports")

        # Construct participant-specific folder name
        session_code = player.session.code
        participant_code = player.participant.code
        participant_id = player.id_in_group
        participant_folder = f"{session_code}_{participant_code}_{participant_id}"

        # Define the PDF file path inside the participant's folder
        pdf_filename = f"{participant_folder}.pdf"
        pdf_path = os.path.join(reports_directory, participant_folder, pdf_filename)

        # Define the URL path to serve the file in the browser
        pdf_url = f"/static/reports/{participant_folder}/{pdf_filename}"  # Path for user download

        # Ensure the file exists before making it available
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF not found at {pdf_path}")

        return {"pdf_url": pdf_url}

class EndSurvey(Page):
    
    @staticmethod              
    def js_vars(player):
        return dict(
            completionlink=
              player.subsession.session.config['completionlink']
        )
    pass

# Updated page sequence without RankingPageA and RankingPageB
page_sequence = [Questions1_v2, GeneratePDFPage, DownloadReport, EndSurvey]